from app.core.config import settings
from app.services import embedding_service, vector_store_service


def retrieve(video_id: str, question: str) -> list[dict]:
    """Return top-k chunks above the similarity threshold, ordered by score."""
    qvec = embedding_service.embed([question])[0]
    hits = vector_store_service.search(video_id, qvec, settings.retrieval_top_k)
    return [{**c, "score": s} for c, s in hits if s >= settings.min_similarity]
