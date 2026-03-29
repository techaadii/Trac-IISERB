"""

Embedding Cache
===============
Pre computes and persists two embeddings per camera image
    - full-embedding: 2048 dim fused embedding -> used for image - to - image search.
    - sem-emb : 512 dim semantic (clip) -> Used for text to image search


"""

"""
EmbeddingCache
==============
Pre-computes and persists two embeddings per camera image:
  - full_emb  : 2048-dim fused embedding  → used for image-to-image search
  - sem_emb   : 512-dim  semantic (CLIP)  → used for text-to-image search

On first run  : scans all camera folders, encodes every image, saves .pkl
On later runs : loads .pkl instantly (< 1 second)
"""

import logging
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms as T
from PIL import Image

from backend.app.core.config import settings
from backend.app.core.camera_network import CAMERAS

logger = logging.getLogger(__name__)

INFERENCE_TRANSFORM = T.Compose([
    T.Resize((256, 256)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406],
                std =[0.229, 0.224, 0.225]),
])


@dataclass
class CacheEntry:
    camera_id:  str
    image_path: str
    full_emb:   np.ndarray    # 2048-dim — image search
    sem_emb:    np.ndarray    # 512-dim  — text search


class EmbeddingCache:

    def __init__(self):
        self.entries: List[CacheEntry] = []
        self._by_camera: Dict[str, List[int]] = {}

    # ── Build / Load ──────────────────────────────────────────────────────────

    def build_or_load(self, force_rebuild: bool = False):
        cache_path = Path(settings.EMBEDDING_CACHE_PATH)

        if cache_path.exists() and not force_rebuild:
            logger.info("Loading embedding cache from %s ...", cache_path)
            self._load(cache_path)
            logger.info("Cache loaded: %d images across %d cameras",
                        len(self.entries), len(self._by_camera))
        else:
            logger.info("Building embedding cache ...")
            self._build()
            self._save(cache_path)
            logger.info("Cache built and saved: %d images", len(self.entries))

    def _build(self):
        from backend.app.core.model_manager import model_manager

        if not model_manager.is_loaded:
            logger.error("Model not loaded — cannot build cache.")
            return

        self.entries    = []
        self._by_camera = {}

        camera_root = Path(settings.CAMERA_ROOT)

        for cam_id, cam in CAMERAS.items():
            cam_folder = camera_root / cam.folder_name
            if not cam_folder.exists():
                logger.warning("Camera folder missing: %s", cam_folder)
                continue

            image_files = []
            for ext in settings.IMAGE_EXTENSIONS:
                image_files.extend(cam_folder.glob(f"*{ext}"))
                image_files.extend(cam_folder.glob(f"*{ext.upper()}"))

            if not image_files:
                logger.warning("No images found in %s", cam_folder)
                continue

            logger.info("Encoding %d images for %s ...", len(image_files), cam_id)

            cam_indices = []
            for img_path in sorted(image_files):
                try:
                    full_emb, sem_emb = self._encode_image(img_path, model_manager)
                    idx = len(self.entries)
                    self.entries.append(CacheEntry(
                        camera_id  = cam_id,
                        image_path = str(img_path),
                        full_emb   = full_emb,
                        sem_emb    = sem_emb,
                    ))
                    cam_indices.append(idx)
                except Exception as e:
                    logger.warning("Failed to encode %s: %s", img_path, e)

            self._by_camera[cam_id] = cam_indices

    @torch.no_grad()
    def _encode_image(self, img_path: Path, model_manager) -> tuple:
        image  = Image.open(img_path).convert("RGB")
        tensor = INFERENCE_TRANSFORM(image).unsqueeze(0).to(model_manager.device)

        m = model_manager.model

        ta       = m.backbone(tensor)               # (1, 2048)
        ts       = m.sem_module(tensor)              # (1, 512)
        ts_bn    = m.sem_bn(ts)                     # (1, 512)
        ts_prime = m.afem(ts_bn)                    # (1, 2048)
        fusion   = m.fusion_module(ta, ts_bn)        # (1, 2048)
        t        = ts_prime + fusion                 # (1, 2048)

        full_emb = F.normalize(t,  p=2, dim=1).squeeze(0).cpu().numpy()
        sem_emb  = F.normalize(ts, p=2, dim=1).squeeze(0).cpu().numpy()

        return full_emb, sem_emb

    # ── Persistence ───────────────────────────────────────────────────────────

    def _save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"entries": self.entries, "by_camera": self._by_camera}, f)

    def _load(self, path: Path):
        with open(path, "rb") as f:
            data = pickle.load(f)
        self.entries    = data["entries"]
        self._by_camera = data["by_camera"]

    # ── Query helpers ─────────────────────────────────────────────────────────

    def get_camera_entries(self, camera_id: str) -> List[CacheEntry]:
        indices = self._by_camera.get(camera_id, [])
        return [self.entries[i] for i in indices]

    def search_camera(
        self,
        camera_id:  str,
        query_emb:  np.ndarray,
        use_sem:    bool = False,
        top_k:      int  = 10,
    ) -> List[dict]:
        entries = self.get_camera_entries(camera_id)
        if not entries:
            return []

        matrix = np.stack([e.sem_emb  if use_sem else e.full_emb for e in entries])
        scores = matrix @ query_emb
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [{
            "camera_id":  entries[i].camera_id,
            "image_path": entries[i].image_path,
            "similarity": float(scores[i]),
        } for i in top_indices]

    def search_all(
        self,
        query_emb: np.ndarray,
        use_sem:   bool = False,
        top_k:     int  = 10,
    ) -> List[dict]:
        if not self.entries:
            return []

        matrix      = np.stack([e.sem_emb if use_sem else e.full_emb for e in self.entries])
        scores      = matrix @ query_emb
        top_indices = np.argsort(scores)[::-1][:top_k]

        return [{
            "camera_id":  self.entries[i].camera_id,
            "image_path": self.entries[i].image_path,
            "similarity": float(scores[i]),
        } for i in top_indices]


# Singleton
embedding_cache = EmbeddingCache()
