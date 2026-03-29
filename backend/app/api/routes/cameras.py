"""
Camera Routes
=============
GET /api/cameras/          — list all cameras with metadata
GET /api/cameras/{id}      — single camera detail
GET /api/cameras/browse    — browse images in a camera folder
"""

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from backend.app.core.camera_network import ADJACENCY, CAMERAS
from backend.app.core.config import settings
from backend.app.core.embedding_cache import embedding_cache
from backend.app.schemas.schemas import CameraInfo, CameraListResponse

logger = logging.getLogger(__name__)
router = APIRouter()


def _camera_to_info(camera_id: str) -> CameraInfo:
    cam         = CAMERAS[camera_id]
    neighbours  = sorted(ADJACENCY.get(camera_id, set()))
    image_count = len(embedding_cache.get_camera_entries(camera_id))

    return CameraInfo(
        camera_id   = camera_id,
        label       = cam.label,
        is_root     = cam.is_root,
        is_terminal = cam.is_terminal,
        neighbours  = neighbours,
        image_count = image_count,
    )


@router.get("/", response_model=CameraListResponse, summary="List all cameras")
async def list_cameras():
    cameras = [_camera_to_info(cam_id) for cam_id in CAMERAS]
    return CameraListResponse(total=len(cameras), cameras=cameras)


@router.get("/browse", summary="Browse images in a camera folder")
async def browse_camera(
    camera_id:    str           = Query(..., description="Camera ID e.g. ENTRY_CAM"),
    vehicle_type: Optional[str] = Query(None, description="Filter by vehicle type (future use)"),
    time_from:    Optional[str] = Query(None, description="Filter from time HH:MM (future use)"),
    time_to:      Optional[str] = Query(None, description="Filter to time HH:MM (future use)"),
    limit:        int           = Query(default=50, ge=1, le=200),
):
    """
    Returns a list of image URLs for a given camera.
    Used by the frontend Browse Root Camera tab.
    """
    if camera_id not in CAMERAS:
        raise HTTPException(404, f"Camera '{camera_id}' not found.")

    cam         = CAMERAS[camera_id]
    cam_folder  = Path(settings.CAMERA_ROOT) / cam.folder_name

    if not cam_folder.exists():
        return {"camera_id": camera_id, "images": [], "total": 0}

    image_files = []
    for ext in settings.IMAGE_EXTENSIONS:
        image_files.extend(cam_folder.glob(f"*{ext}"))
        image_files.extend(cam_folder.glob(f"*{ext.upper()}"))

    image_files = sorted(image_files)[:limit]

    images = [
        {
            "filename":  f.name,
            "url":       f"/static/cameras/{cam.folder_name}/{f.name}",
            "camera_id": camera_id,
        }
        for f in image_files
    ]

    return {
        "camera_id": camera_id,
        "label":     cam.label,
        "images":    images,
        "total":     len(images),
    }


@router.get("/{camera_id}", response_model=CameraInfo, summary="Single camera detail")
async def get_camera(camera_id: str):
    if camera_id not in CAMERAS:
        raise HTTPException(404, f"Camera '{camera_id}' not found.")
    return _camera_to_info(camera_id)