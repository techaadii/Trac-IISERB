"""
main.py
=======
FastAPI application entry point.

Startup sequence:
  1. Init HMM SQLite database
  2. Load CLIP_SENet model into memory
  3. Build or load embedding cache
  4. Run initial Hikvision camera health check
  5. Start background health check loop

All routes are registered here with their URL prefixes.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes import cameras, hmm, search
from backend.app.api.routes import live
from backend.app.core.config import settings
from backend.app.core.embedding_cache import embedding_cache
from backend.app.core.hmm_engine import init_db
from backend.app.core.model_manager import model_manager
from backend.app.services.live_stream_service import live_stream_service

logging.basicConfig(
    level   = logging.INFO,
    format  = "%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    datefmt = "%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Everything before 'yield' runs at startup.
    Everything after 'yield' runs at shutdown.
    """

    # ── STARTUP ───────────────────────────────────────────────────────────────
    logger.info("=" * 55)
    logger.info("  TRAC-IISERB Backend Starting Up")
    logger.info("=" * 55)

    # 1. Init HMM database
    logger.info("[1/4] Initialising HMM database ...")
    init_db()

    # 2. Load CLIP_SENet model
    logger.info("[2/4] Loading CLIP_SENet model ...")
    await model_manager.load()

    # 3. Build or load embedding cache
    if model_manager.is_loaded:
        logger.info("[3/4] Loading embedding cache ...")
        embedding_cache.build_or_load()
    else:
        logger.warning("[3/4] Model not loaded — skipping cache build.")
        logger.warning("      Search will not work until model is available.")

    # 4. Camera health check + background loop
    logger.info("[4/4] Checking Hikvision camera network ...")
    await live_stream_service.check_all_cameras()
    health_task = asyncio.create_task(live_stream_service.start_health_loop())

    logger.info("=" * 55)
    logger.info("  Startup complete. API ready at http://localhost:8000")
    logger.info("  Docs available at http://localhost:8000/docs")
    logger.info("=" * 55)

    yield   # ← server runs here

    # ── SHUTDOWN ──────────────────────────────────────────────────────────────
    logger.info("Shutting down ...")
    health_task.cancel()
    await model_manager.unload()
    logger.info("Shutdown complete.")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title       = "TRAC-IISERB API",
    description = "Multi-camera vehicle tracking · CLIP_SENet + HMM · IISER Bhopal",
    version     = "1.0.0",
    lifespan    = lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allows the Next.js frontend (localhost:3000) to call this backend

app.add_middleware(
    CORSMiddleware,
    allow_origins     = settings.ALLOWED_ORIGINS,
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

# ── Static files ──────────────────────────────────────────────────────────────
# Camera images are served at /static/cameras/<folder>/<filename>
# e.g. /static/cameras/entry_cam/img001.jpg

camera_root = Path(settings.CAMERA_ROOT)
camera_root.mkdir(parents=True, exist_ok=True)

app.mount(
    "/static/cameras",
    StaticFiles(directory=str(camera_root)),
    name="cameras",
)

# ── Routes ────────────────────────────────────────────────────────────────────

app.include_router(search.router,  prefix="/api/search",  tags=["Search"])
app.include_router(cameras.router, prefix="/api/cameras", tags=["Cameras"])
app.include_router(hmm.router,     prefix="/api/hmm",     tags=["HMM"])
app.include_router(live.router,    prefix="/api/live",    tags=["Live Streams"])


# ── Health endpoint ───────────────────────────────────────────────────────────

@app.get("/api/health", tags=["Health"], summary="Server health check")
async def health():
    from backend.app.services.live_stream_service import status_cache
    return {
        "status":           "online",
        "model_loaded":     model_manager.is_loaded,
        "images_cached":    len(embedding_cache.entries),
        "cameras_online":   status_cache.online_count,
        "cameras_total":    len(__import__(
            'backend.app.core.camera_network',
            fromlist=['CAMERAS']
        ).CAMERAS),
    }