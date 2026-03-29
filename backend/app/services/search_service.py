"""
search_service.py
=================
Core search logic — compares a query embedding against the cache.
Called by sequential_search_service one camera at a time.
"""

import logging
from pathlib import Path
from typing import List, Optional

import numpy as np

from backend.app.core.config import settings
from backend.app.core.embedding_cache import embedding_cache
from backend.app.core.camera_network import CAMERAS
from backend.app.schemas.schemas import SearchResult, CameraSearchResult

logger = logging.getLogger(__name__)


def _make_image_url(image_path: str) -> str:
    try:
        p = Path(image_path)
        parts = p.parts
        cam_idx = next(
            (i for i, part in enumerate(parts) if part == "cameras"), None
        )
        if cam_idx is not None:
            relative = "/".join(parts[cam_idx:])
            return f"/static/{relative}"
    except Exception:
        pass
    return image_path


def search_camera(
    camera_id:  str,
    query_emb:  np.ndarray,
    use_sem:    bool = False,
    top_k:      int  = 10,
    threshold:  Optional[float] = None,
) -> CameraSearchResult:
    min_score = threshold if threshold is not None else settings.SIMILARITY_THRESHOLD
    cam_label = CAMERAS[camera_id].label if camera_id in CAMERAS else camera_id

    raw_results = embedding_cache.search_camera(
        camera_id = camera_id,
        query_emb = query_emb,
        use_sem   = use_sem,
        top_k     = top_k,
    )

    hits = []
    for r in raw_results:
        if r["similarity"] < min_score:
            continue
        hits.append(SearchResult(
            camera_id  = r["camera_id"],
            image_path = r["image_path"],
            similarity = round(r["similarity"], 4),
            image_url  = _make_image_url(r["image_path"]),
        ))

    best_score = hits[0].similarity if hits else 0.0

    return CameraSearchResult(
        camera_id  = camera_id,
        label      = cam_label,
        hits       = hits,
        best_score = best_score,
        searched   = True,
    )


def search_all_cameras(
    query_emb:  np.ndarray,
    use_sem:    bool = False,
    top_k:      int  = 10,
    threshold:  Optional[float] = None,
) -> List[CameraSearchResult]:
    results = []
    for camera_id in CAMERAS:
        result = search_camera(
            camera_id = camera_id,
            query_emb = query_emb,
            use_sem   = use_sem,
            top_k     = top_k,
            threshold = threshold,
        )
        results.append(result)

    results.sort(key=lambda x: x.best_score, reverse=True)
    return results


def get_top_results(
    camera_results: List[CameraSearchResult],
    top_k: int = 10,
) -> List[SearchResult]:
    all_hits = []
    for cr in camera_results:
        all_hits.extend(cr.hits)

    all_hits.sort(key=lambda x: x.similarity, reverse=True)
    return all_hits[:top_k]
