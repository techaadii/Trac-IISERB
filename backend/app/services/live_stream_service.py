"""
live_stream_service.py
======================
Handles health checks and stream proxying for Hikvision cameras.
"""

import asyncio
import logging
import time
from typing import Dict, Optional

import httpx

from backend.app.core.hikvision_config import HIKVISION_CAMERAS, HikvisionCamera

logger = logging.getLogger(__name__)

HEALTH_CHECK_INTERVAL = 15
SNAPSHOT_TIMEOUT      = 5
STREAM_TIMEOUT        = 30


class CameraStatusCache:
    def __init__(self):
        self._status: Dict[str, Dict] = {
            cam_id: {"online": False, "last_checked": 0.0, "latency_ms": None}
            for cam_id in HIKVISION_CAMERAS
        }
        self._lock = asyncio.Lock()

    async def update(self, camera_id: str, online: bool, latency_ms: Optional[int] = None):
        async with self._lock:
            self._status[camera_id] = {
                "online":       online,
                "last_checked": time.time(),
                "latency_ms":   latency_ms,
            }

    def get(self, camera_id: str) -> Dict:
        return self._status.get(
            camera_id,
            {"online": False, "last_checked": 0.0, "latency_ms": None}
        )

    def all(self) -> Dict[str, Dict]:
        return dict(self._status)

    @property
    def online_count(self) -> int:
        return sum(1 for s in self._status.values() if s["online"])

    @property
    def offline_count(self) -> int:
        return sum(1 for s in self._status.values() if not s["online"])


status_cache = CameraStatusCache()


class LiveStreamService:

    async def check_camera(self, cam: HikvisionCamera) -> bool:
        t0 = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=SNAPSHOT_TIMEOUT) as client:
                r  = await client.get(cam.snapshot_url)
                ok = r.status_code == 200 and len(r.content) > 1000
                latency = int((time.monotonic() - t0) * 1000)
                await status_cache.update(cam.camera_id, ok, latency if ok else None)
                return ok
        except Exception as exc:
            logger.debug("Camera %s unreachable: %s", cam.camera_id, exc)
            await status_cache.update(cam.camera_id, False)
            return False

    async def check_all_cameras(self):
        tasks   = [self.check_camera(cam) for cam in HIKVISION_CAMERAS.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        online  = sum(1 for r in results if r is True)
        logger.info("Camera health check: %d/%d online", online, len(HIKVISION_CAMERAS))

    async def start_health_loop(self):
        while True:
            await self.check_all_cameras()
            await asyncio.sleep(HEALTH_CHECK_INTERVAL)

    async def get_snapshot(self, camera_id: str) -> Optional[bytes]:
        cam = HIKVISION_CAMERAS.get(camera_id)
        if not cam:
            return None
        try:
            async with httpx.AsyncClient(timeout=SNAPSHOT_TIMEOUT) as client:
                r = await client.get(cam.snapshot_url)
                if r.status_code == 200:
                    await status_cache.update(camera_id, True)
                    return r.content
        except Exception as exc:
            logger.debug("Snapshot failed for %s: %s", camera_id, exc)
            await status_cache.update(camera_id, False)
        return None

    async def stream_mjpeg(self, camera_id: str):
        cam = HIKVISION_CAMERAS.get(camera_id)
        if not cam:
            return
        async with httpx.AsyncClient(timeout=httpx.Timeout(STREAM_TIMEOUT)) as client:
            try:
                async with client.stream("GET", cam.mjpeg_url) as response:
                    await status_cache.update(camera_id, True)
                    async for chunk in response.aiter_bytes(chunk_size=4096):
                        yield chunk
            except Exception as exc:
                logger.warning("MJPEG stream error for %s: %s", camera_id, exc)
                await status_cache.update(camera_id, False)

    def get_all_status(self) -> Dict:
        statuses = []
        for cam_id, cam in HIKVISION_CAMERAS.items():
            s = status_cache.get(cam_id)
            statuses.append({
                "camera_id":    cam_id,
                "label":        cam.label,
                "ip":           cam.ip,
                "online":       s["online"],
                "last_checked": s["last_checked"],
                "latency_ms":   s["latency_ms"],
                "snapshot_url": f"/api/live/{cam_id}/snapshot",
                "mjpeg_url":    f"/api/live/{cam_id}/stream",
            })
        return {
            "online_count":  status_cache.online_count,
            "offline_count": status_cache.offline_count,
            "total":         len(HIKVISION_CAMERAS),
            "cameras":       statuses,
        }


live_stream_service = LiveStreamService()
