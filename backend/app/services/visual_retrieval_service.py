"""Visual retrieval: text question -> CLIP text embedding -> search frame index.

Kept separate from the transcript retrieval modules.
"""
import re

from app.core.config import settings
from app.services import clip_service, storage_service as storage

VISUAL_WORDS = re.compile(
    r"\b(diagram|slide|chart|graph|schema|screen|screenshot|frame|image|picture|figure|"
    r"draw|drawn|drew|shown|show|shows|showing|display|visual|architecture|table|code on)\b",
    re.I,
)
TIMECODE = re.compile(r"\b(?:(\d{1,2}):)?(\d{1,2}):(\d{2})\b")


def has_visual_intent(question: str) -> bool:
    return bool(VISUAL_WORDS.search(question))


def parse_timecodes(question: str) -> list[float]:
    """Explicit timestamps in the question, e.g. 'at 12:30' or '1:02:03'."""
    out = []
    for h, m, s in TIMECODE.findall(question):
        if int(s) < 60:
            out.append(int(h or 0) * 3600 + int(m) * 60 + int(s))
    return out


def build_index(video_id: str, frames: list[dict]) -> None:
    import faiss

    frame_dir = storage.path_for("frames", video_id, "")
    vectors = clip_service.embed_images([frame_dir / f"{f['id']}.jpg" for f in frames])
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    faiss.write_index(index, str(storage.path_for("indexes", video_id, ".visual.faiss")))
    storage.write_json(storage.path_for("indexes", video_id, ".frames.json"), frames)


def load_frames(video_id: str) -> list[dict]:
    return storage.read_json(storage.path_for("indexes", video_id, ".frames.json"))


def search_text(video_id: str, question: str) -> list[dict]:
    """Frames semantically matching the question, filtered by similarity threshold."""
    import faiss

    frames = load_frames(video_id)
    index = faiss.read_index(str(storage.path_for("indexes", video_id, ".visual.faiss")))
    qvec = clip_service.embed_text([question])
    intent = has_visual_intent(question)
    threshold = settings.visual_intent_min_similarity if intent else settings.visual_min_similarity
    k = settings.visual_top_k if intent else max(1, settings.visual_top_k // 2)
    scores, ids = index.search(qvec, min(k, len(frames)))
    return [{**frames[i], "score": float(s), "match": "semantic"}
            for s, i in zip(scores[0], ids[0]) if i >= 0 and s >= threshold]


def frames_near(video_id: str, seconds: float, tolerance: float = 45.0) -> list[dict]:
    """Closest indexed frame to an explicitly requested timestamp."""
    frames = load_frames(video_id)
    if not frames:
        return []
    best = min(frames, key=lambda f: abs(f["timestamp"] - seconds))
    if abs(best["timestamp"] - seconds) > tolerance:
        return []
    return [{**best, "score": 1.0, "match": "timestamp"}]


def retrieve(video_id: str, question: str) -> list[dict]:
    hits: dict[str, dict] = {}
    for t in parse_timecodes(question):
        for f in frames_near(video_id, t):
            hits[f["id"]] = f
    for f in search_text(video_id, question):
        hits.setdefault(f["id"], f)
    return sorted(hits.values(), key=lambda f: f["timestamp"])
