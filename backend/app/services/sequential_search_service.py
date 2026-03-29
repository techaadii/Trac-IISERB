"""
sequential_search_service.py
=============================
Orchestrates the full HMM-guided sequential camera search.

Flow:
  1. Encode query (image or text)
  2. Start at ENTRY_CAM
  3. Search that camera → record (camera_id, best_score) as HMM observation
  4. Ask HMM for next most likely camera
  5. Repeat until EXIT_CAM or all reachable cameras visited
  6. Run Viterbi on observations → decode most likely path
  7. Return full SearchSession
"""

import logging
import uuid
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image

from backend.app.core.camera_network import (
    CAMERAS, ROOT_CAMERA, TERMINAL_CAMERA, bfs_order
)
from backend.app.core.hmm_engine import ranked_cameras, viterbi
from backend.app.core.model_manager import model_manager
from backend.app.schemas.schemas import (
    CameraSearchResult, SearchSession
)
from backend.app.services.search_service import (
    get_top_results, search_camera
)

logger = logging.getLogger(__name__)

# Max cameras to visit per search session
# Prevents infinite loops on edge cases
MAX_CAMERAS = len(CAMERAS)


class SequentialSearchService:

    # ── Public entry points ───────────────────────────────────────────────────

    async def search_by_image(
        self,
        image: Image.Image,
        top_k: int = 10,
    ) -> SearchSession:
        """
        Full sequential search from an uploaded query image.
        Uses 2048-dim full embedding for camera comparisons.
        """
        if not model_manager.is_loaded:
            raise RuntimeError("Model not loaded.")

        logger.info("Starting image search session ...")
        query_emb = model_manager.encode_image(image)

        return await self._run_sequential_search(
            query_emb  = query_emb,
            use_sem    = False,
            query_type = "image",
            query_text = None,
            top_k      = top_k,
        )

    async def search_by_text(
        self,
        query_text: str,
        top_k:      int = 10,
    ) -> SearchSession:
        """
        Full sequential search from a text description.
        Uses 512-dim semantic embedding for camera comparisons.
        """
        if not model_manager.is_loaded:
            raise RuntimeError("Model not loaded.")

        logger.info("Starting text search: '%s' ...", query_text)
        query_emb = model_manager.encode_text(query_text)

        return await self._run_sequential_search(
            query_emb  = query_emb,
            use_sem    = True,
            query_type = "text",
            query_text = query_text,
            top_k      = top_k,
        )

    # ── Core sequential logic ─────────────────────────────────────────────────

    async def _run_sequential_search(
        self,
        query_emb:  np.ndarray,
        use_sem:    bool,
        query_type: str,
        query_text: Optional[str],
        top_k:      int,
    ) -> SearchSession:

        session_id   = str(uuid.uuid4())[:8]
        visited      = set()
        observations : List[Tuple[str, float]] = []
        cam_results  : List[CameraSearchResult] = []

        # Always start at entry camera
        current_cam = ROOT_CAMERA

        for step in range(MAX_CAMERAS):

            if current_cam in visited:
                logger.debug("Step %d: %s already visited, stopping.", step, current_cam)
                break

            visited.add(current_cam)
            logger.info("Step %d: searching camera %s ...", step, current_cam)

            # ── Search this camera ────────────────────────────────────────────
            result = search_camera(
                camera_id = current_cam,
                query_emb = query_emb,
                use_sem   = use_sem,
                top_k     = top_k,
            )
            cam_results.append(result)

            # ── Record observation for Viterbi ────────────────────────────────
            # Observation = (camera_id, best similarity score at this camera)
            # If no hits, score = 0 (vehicle likely not here)
            obs_score = result.best_score if result.hits else 0.0
            observations.append((current_cam, obs_score))

            logger.info(
                "  → %d hits, best score %.3f", len(result.hits), obs_score
            )

            # ── Stop at terminal camera ───────────────────────────────────────
            if current_cam == TERMINAL_CAMERA:
                logger.info("Reached EXIT_CAM — stopping search.")
                break

            # ── Ask HMM for next camera ───────────────────────────────────────
            next_cam = self._pick_next_camera(current_cam, visited)
            if next_cam is None:
                logger.info("No unvisited neighbours from %s — stopping.", current_cam)
                break

            current_cam = next_cam

        # ── Viterbi decode ────────────────────────────────────────────────────
        viterbi_path = viterbi(observations, start_cam=ROOT_CAMERA)
        logger.info("Viterbi path: %s", " → ".join(viterbi_path))

        # ── Build final top-K results ─────────────────────────────────────────
        top_results = get_top_results(cam_results, top_k=top_k)

        total_images = sum(
            len(cr.hits) for cr in cam_results
        )

        return SearchSession(
            session_id             = session_id,
            query_type             = query_type,
            query_text             = query_text,
            cameras_queried        = cam_results,
            viterbi_path           = viterbi_path,
            top_results            = top_results,
            total_images_searched  = total_images,
        )

    # ── HMM camera selection ──────────────────────────────────────────────────

    def _pick_next_camera(
        self,
        current_cam: str,
        visited:     set,
    ) -> Optional[str]:
        """
        Ask the HMM which unvisited neighbour to check next.

        ranked_cameras() returns neighbours sorted by transition
        probability descending. On cold start all are equal so
        we just pick the first alphabetically.

        We skip already-visited cameras.
        """
        ranked = ranked_cameras(current_cam)

        for cam_id, prob in ranked:
            if cam_id not in visited:
                logger.debug(
                    "  HMM picks %s (prob=%.3f) from %s",
                    cam_id, prob, current_cam
                )
                return cam_id

        # All neighbours visited — fall back to BFS order
        bfs = bfs_order(current_cam)
        for cam_id in bfs:
            if cam_id not in visited and cam_id != current_cam:
                return cam_id

        return None


# Singleton
sequential_search_service = SequentialSearchService()