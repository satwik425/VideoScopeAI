from functools import lru_cache

import numpy as np

from app.core.config import settings


@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.embedding_model)


def embed(texts: list[str]) -> np.ndarray:
    vecs = _model().encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    return np.asarray(vecs, dtype="float32")
