"""
Live Stream Routes
==================
GET  /api/live/status              — all camera online/offline status
GET  /api/live/{camera_id}/status  — single camera status
GET  /api/live/{camera_id}/snapshot — single JPEG (for polling)
GET  /api/live/{camera_id}/stream   — proxied MJPEG stream
POST /api/live/refresh             — force immediate health check
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse

from backend.app.services.live_stream_service import live_stream_service

router = APIRouter()


@router.get("/status", summary="All cameras online/offline status + counts")
async def get_all_status():
    return live_stream_service.get_all_status()


@router.get("/{camera_id}/status", summary="Single camera status")
async def get_camera_status(camera_id: str):
    from backend.app.core.hikvision_config import HIKVISION_CAMERAS
    if camera_id not in HIKVISION_CAMERAS:
        raise HTTPException(404, f"Camera '{camera_id}' not found.")
    from backend.app.services.live_stream_service import status_cache
    s   = status_cache.get(camera_id)
    cam = HIKVISION_CAMERAS[camera_id]
    return {
        "camera_id":    camera_id,
        "label":        cam.label,
        "online":       s["online"],
        "last_checked": s["last_checked"],
        "latency_ms":   s["latency_ms"],
    }


@router.get("/{camera_id}/snapshot", summary="Fetch latest JPEG snapshot from camera")
async def get_snapshot(camera_id: str):
    data = await live_stream_service.get_snapshot(camera_id)
    if data is None:
        raise HTTPException(503, f"Camera '{camera_id}' is offline or unreachable.")
    return Response(content=data, media_type="image/jpeg")


@router.get("/{camera_id}/stream", summary="Proxy MJPEG live stream")
async def stream_camera(camera_id: str):
    from backend.app.core.hikvision_config import HIKVISION_CAMERAS
    if camera_id not in HIKVISION_CAMERAS:
        raise HTTPException(404, f"Camera '{camera_id}' not found.")
    return StreamingResponse(
        live_stream_service.stream_mjpeg(camera_id),
        media_type="multipart/x-mixed-replace; boundary=--myboundary",
    )


@router.post("/refresh", summary="Force immediate health check on all cameras")
async def force_refresh():
    await live_stream_service.check_all_cameras()
    return live_stream_service.get_all_status()
