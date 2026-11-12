import numpy as np

from app.services import storage_service as storage


def build_index(video_id: str, chunks: list[dict], vectors: np.ndarray) -> None:
    import faiss

    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(storage.path_for("indexes", video_id, ".faiss")))
    storage.write_json(storage.path_for("indexes", video_id, ".chunks.json"), chunks)


def search(video_id: str, query_vec: np.ndarray, k: int) -> list[tuple[dict, float]]:
    import faiss
    idx_path = storage.path_for("indexes", video_id, ".faiss")
    index = faiss.read_index(str(idx_path))
    chunks = storage.read_json(storage.path_for("indexes", video_id, ".chunks.json"))
    scores, ids = index.search(query_vec.reshape(1, -1), min(k, len(chunks)))
    return [(chunks[i], float(s)) for s, i in zip(scores[0], ids[0]) if i >= 0]

