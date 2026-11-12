"""CLIP image/text encoders (Hugging Face Transformers + PyTorch).

Image and text embeddings live in the same space, so a text question can be matched
directly against frame embeddings. Vectors are L2-normalised so FAISS inner product
equals cosine similarity.
"""
from functools import lru_cache
from pathlib import Path
import threading

import numpy as np

from app.core.config import settings

_lock = threading.Lock()


@lru_cache(maxsize=1)
def _load_unlocked():
    import torch
    from transformers import CLIPModel, CLIPProcessor

    model = CLIPModel.from_pretrained(settings.clip_model).eval()
    processor = CLIPProcessor.from_pretrained(settings.clip_model)
    return torch, model, processor


def _load():
    with _lock:
        return _load_unlocked()


def _as_tensor(out):
    """Transformers versions differ: tensor vs. output object."""
    if hasattr(out, "pooler_output") and out.pooler_output is not None:
        return out.pooler_output
    return out


def _normalise(t) -> np.ndarray:
    v = t.detach().cpu().numpy().astype("float32")
    return v / np.clip(np.linalg.norm(v, axis=1, keepdims=True), 1e-12, None)


def embed_images(paths: list[Path], batch_size: int = 16) -> np.ndarray:
    from PIL import Image

    torch, model, processor = _load()
    out = []
    for i in range(0, len(paths), batch_size):
        images = []
        for p in paths[i:i + batch_size]:
            with Image.open(p) as im:
                images.append(im.convert("RGB"))
        inputs = processor(images=images, return_tensors="pt")
        with torch.no_grad():
            out.append(_normalise(_as_tensor(model.get_image_features(**inputs))))
    return np.concatenate(out)


def embed_text(texts: list[str]) -> np.ndarray:
    torch, model, processor = _load()
    inputs = processor(text=texts, return_tensors="pt", padding=True, truncation=True, max_length=77)
    with torch.no_grad():
        return _normalise(_as_tensor(model.get_text_features(**inputs)))
