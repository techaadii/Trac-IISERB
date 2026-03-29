"""
Search Routes
=============
POST /api/search/image  — upload query image → sequential search
POST /api/search/text   — text description  → sequential search
POST /api/search/rebuild-cache — force re-encode all camera images
"""

import logging
from io import BytesIO

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from PIL import Image

from backend.app.schemas.schemas import SearchSession, TextSearchRequest
from backend.app.services.sequential_search_service import sequential_search_service
from backend.app.core.embedding_cache import embedding_cache

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/image", response_model=SearchSession, summary="Search by query image")
async def search_by_image(
    file:  UploadFile = File(..., description="Query vehicle image (jpg/png)"),
    top_k: int        = Form(default=10, ge=1, le=50),
):
    """
    Upload a vehicle image.
    Runs full HMM-guided sequential search across all cameras.
    Returns ranked matches + Viterbi-decoded path.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image.")

    try:
        contents = await file.read()
        image    = Image.open(BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(400, f"Could not read image: {e}")

    try:
        session = await sequential_search_service.search_by_image(
            image = image,
            top_k = top_k,
        )
    except RuntimeError as e:
        raise HTTPException(503, str(e))

    return session


@router.post("/text", response_model=SearchSession, summary="Search by text description")
async def search_by_text(request: TextSearchRequest):
    """
    Describe the vehicle in plain text e.g. 'red Honda sedan near hostel'.
    Runs full HMM-guided sequential search using CLIP text encoder.
    Returns ranked matches + Viterbi-decoded path.
    """
    try:
        session = await sequential_search_service.search_by_text(
            query_text = request.query,
            top_k      = request.top_k,
        )
    except RuntimeError as e:
        raise HTTPException(503, str(e))

    return session


@router.post("/rebuild-cache", summary="Force rebuild embedding cache")
async def rebuild_cache():
    """
    Re-encodes all camera images and saves new cache to disk.
    Call this after adding new images to any camera folder.
    Takes a few minutes depending on image count.
    """
    try:
        embedding_cache.build_or_load(force_rebuild=True)
        return {
            "success":      True,
            "total_images": len(embedding_cache.entries),
            "cameras":      len(embedding_cache._by_camera),
        }
    except Exception as e:
        raise HTTPException(500, f"Cache rebuild failed: {e}")