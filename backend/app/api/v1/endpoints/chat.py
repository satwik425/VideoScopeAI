import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.endpoints.videos import get_video_or_404
from app.db.models import ChatMessage
from app.db.session import get_db
from app.schemas.schemas import ChatRequest, ChatResponse, Evidence, FrameEvidence
from app.services import llm_service, retrieval_service, storage_service as storage
from app.services import visual_retrieval_service

log = logging.getLogger("vidscope.chat")
router = APIRouter()

NO_EVIDENCE = ("I couldn't find anything in this video's transcript or frames that answers that question. "
               "Try rephrasing, or ask about something shown or discussed in the video.")
SPEECH_WINDOW = 15.0  # seconds of transcript context around a frame


def _nearby_text(chunks: list[dict], t: float) -> str:
    near = [c for c in chunks if c["start_seconds"] - SPEECH_WINDOW <= t <= c["end_seconds"] + SPEECH_WINDOW]
    near.sort(key=lambda c: abs((c["start_seconds"] + c["end_seconds"]) / 2 - t))
    return near[0]["text"] if near else ""


def _retrieve_frames(video, question: str) -> list[dict]:
    """Visual retrieval is best-effort; it must never break transcript Q&A."""
    if video.visual_status != "ready":
        return []
    try:
        frames = visual_retrieval_service.retrieve(video.id, question)
        chunks = storage.read_json(storage.path_for("indexes", video.id, ".chunks.json"))
        frame_dir = storage.path_for("frames", video.id, "")
        for f in frames:
            f["nearby_text"] = _nearby_text(chunks, f["timestamp"])
            f["image_path"] = frame_dir / f"{f['id']}.jpg"
        return frames
    except Exception:
        log.exception("visual retrieval failed for %s", video.id)
        return []


@router.post("/videos/{video_id}/chat", response_model=ChatResponse)
def chat(video_id: str, req: ChatRequest, db: Session = Depends(get_db)):
    video = get_video_or_404(db, video_id)
    if video.status != "ready":
        raise HTTPException(409, "Video is not ready")

    hits = retrieval_service.retrieve(video_id, req.question)
    frames = _retrieve_frames(video, req.question)
    history = []
    if req.conversation_id:
        rows = (db.query(ChatMessage)
                .filter_by(video_id=video_id, conversation_id=req.conversation_id)
                .order_by(ChatMessage.id.desc()).limit(6).all())
        history = [{"role": r.role, "content": r.content} for r in reversed(rows)]

    if not hits and not frames:
        answer, status, evidence, visual = NO_EVIDENCE, "insufficient_evidence", [], []
    else:
        try:
            answer = llm_service.generate_answer(req.question, hits, history, frames)
            status = "answered"
        except llm_service.LLMError:
            # Degrade gracefully: still show the retrieved moments.
            answer = ("The AI answer service is unavailable right now, so here are the most "
                      "relevant moments from the video. Click a timestamp to jump there.")
            status = "llm_unavailable"
        evidence = [Evidence(chunk_id=h["id"], start_seconds=h["start_seconds"],
                             end_seconds=h["end_seconds"], text=h["text"]) for h in hits]
        evidence.sort(key=lambda e: e.start_seconds)
        visual = [FrameEvidence(frame_id=f["id"], timestamp_seconds=f["timestamp"], score=f["score"],
                                match=f["match"], nearby_text=f.get("nearby_text", "")) for f in frames]

    db.add(ChatMessage(video_id=video_id, conversation_id=req.conversation_id, role="user", content=req.question))
    db.add(ChatMessage(video_id=video_id, conversation_id=req.conversation_id, role="assistant", content=answer))
    db.commit()
    return ChatResponse(answer=answer, status=status, evidence=evidence, visual_evidence=visual)
