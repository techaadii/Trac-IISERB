"""
ModelManager
============
Loads the full CLIP_SENet model from your .pth checkpoint.

At inference we never call forward(images, labels) directly because
labels don't exist. Instead we:
  - Image query  → run each submodule manually to get embedding t
  - Text query   → use sem_module.clip text encoder directly

The embedding vector 't' (shape: feat_dim,) is what gets stored in
the cache and compared at search time via cosine similarity.
"""

import logging
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import torch
import torch.nn.functional as F
import torchvision.transforms as T
from PIL import Image

logger = logging.getLogger(__name__)

MODEL_CFG = SimpleNamespace(
    clip_model_name = "openai/clip-vit-base-patch32",
    clip_dim        = 512,
    feat_dim        = 2048,
    num_classes     = 1000,
    device          = "cuda" if torch.cuda.is_available() else "cpu",
)

WEIGHTS_PATH = Path("/home/moonlab/Reid/notebooks/latest_model.pth")

INFERENCE_TRANSFORM = T.Compose([
    T.Resize((256, 256)),
    T.ToTensor(),
    T.Normalize(mean=[0.485, 0.456, 0.406],
                std =[0.229, 0.224, 0.225]),
])


class ModelManager:

    def __init__(self):
        self.model     = None
        self.device    = MODEL_CFG.device
        self.is_loaded = False

    async def load(self):
        reid_path = str(WEIGHTS_PATH.parent)
        if reid_path not in sys.path:
            sys.path.insert(0, reid_path)

        try:
            from model import CLIP_SENet
        except ImportError as e:
            logger.error("Could not import CLIP_SENet: %s", e)
            logger.error("Make sure your model .py file is in %s", reid_path)
            return

        logger.info("Instantiating CLIP_SENet on %s ...", self.device)
        self.model = CLIP_SENet(MODEL_CFG).to(self.device)

        logger.info("Loading weights from %s ...", WEIGHTS_PATH)
        state_dict = torch.load(WEIGHTS_PATH, map_location=self.device)
        missing, unexpected = self.model.load_state_dict(state_dict, strict=False)

        if missing:
            logger.warning("Missing keys (%d): %s ...", len(missing), missing[:5])
        if unexpected:
            logger.warning("Unexpected keys (%d): %s ...", len(unexpected), unexpected[:5])

        self.model.eval()
        self.is_loaded = True
        logger.info("CLIP_SENet ready on %s", self.device)

    async def unload(self):
        self.model     = None
        self.is_loaded = False
        logger.info("Model unloaded.")

    @torch.no_grad()
    def encode_image(self, image: Image.Image) -> np.ndarray:
        self._check_loaded()
        tensor   = INFERENCE_TRANSFORM(image).unsqueeze(0).to(self.device)
        m        = self.model
        ta       = m.backbone(tensor)
        ts       = m.sem_module(tensor)
        ts_bn    = m.sem_bn(ts)
        ts_prime = m.afem(ts_bn)
        fusion   = m.fusion_module(ta, ts_bn)
        t        = ts_prime + fusion
        t        = F.normalize(t, p=2, dim=1)
        return t.squeeze(0).cpu().numpy()

    @torch.no_grad()
    def encode_text(self, text: str) -> np.ndarray:
        self._check_loaded()
        from transformers import CLIPTokenizer
        tokenizer = CLIPTokenizer.from_pretrained(MODEL_CFG.clip_model_name)
        inputs    = tokenizer(text, return_tensors="pt",
                              padding=True, truncation=True).to(self.device)
        clip      = self.model.sem_module.clip
        outputs   = clip.get_text_features(**inputs)
        outputs   = F.normalize(outputs, p=2, dim=1)
        return outputs.squeeze(0).cpu().numpy()

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b))

    def _check_loaded(self):
        if not self.is_loaded:
            raise RuntimeError("Model not loaded. Check startup logs.")


model_manager = ModelManager()
