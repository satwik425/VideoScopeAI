import re
import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import ChatMessage, Video
from app.db.session import get_db
from app.schemas.schemas import StatusOut, UploadResponse, VideoOut
from app.services import storage_service as storage
from app.workers.video_tasks import process_video, process_visual

router = APIRouter()


def get_video_or_404(db: Session, video_id: str) -> Video:
    v = db.get(Video, video_id)
    if v is None:
        raise HTTPException(404, "Video not found")
    return v


@router.get("/config")
def config():
    return {"max_upload_mb": settings.max_upload_mb,
            "allowed_extensions": list(settings.allowed_extensions)}


@router.post("/videos", response_model=UploadResponse)
async def upload_video(background: BackgroundTasks, file: UploadFile = File(...),
                       db: Session = Depends(get_db)):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(415, "Unsupported file type")
    if file.content_type and not file.content_type.startswith(("video/", "application/octet-stream")):
        raise HTTPException(415, "Unsupported content type")

    video_id = str(uuid.uuid4())
    dest = storage.path_for("originals", video_id, ext)
    limit = settings.max_upload_mb * 1024 * 1024
    size = 0
    with dest.open("wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > limit:
                out.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB limit")
            out.write(chunk)

    db.add(Video(id=video_id, original_filename=Path(file.filename).name, stored_path=str(dest),
                 content_type=file.content_type or "", size_bytes=size, status="queued"))
    db.commit()
    background.add_task(process_video, video_id)
    return UploadResponse(video_id=video_id, filename=Path(file.filename).name, status="queued")


@router.get("/videos/{video_id}", response_model=VideoOut)
def get_video(video_id: str, db: Session = Depends(get_db)):
    v = get_video_or_404(db, video_id)
    return VideoOut(video_id=v.id, filename=v.original_filename, content_type=v.content_type,
                    size_bytes=v.size_bytes, duration_seconds=v.duration_seconds,
                    status=v.status, stage=v.processing_stage, error_code=v.error_code)


@router.get("/videos/{video_id}/status", response_model=StatusOut)
def get_status(video_id: str, background: BackgroundTasks, db: Session = Depends(get_db)):
    v = get_video_or_404(db, video_id)
    if v.status == "ready" and v.visual_status == "pending":
        v.visual_status = "processing"
        db.commit()
        background.add_task(process_visual, video_id)
    return StatusOut(video_id=v.id, status=v.status, stage=v.processing_stage,
                     progress=v.progress, error_code=v.error_code, visual_status=v.visual_status)


@router.get("/videos/{video_id}/frames/{frame_id}.jpg")
def get_frame(video_id: str, frame_id: str, db: Session = Depends(get_db)):
    get_video_or_404(db, video_id)
    if not re.fullmatch(r"frame-\d{4}", frame_id):
        raise HTTPException(404, "Frame not found")
    path = storage.path_for("frames", video_id, "") / f"{frame_id}.jpg"
    if not path.is_file():
        raise HTTPException(404, "Frame not found")
    return FileResponse(path, media_type="image/jpeg")


@router.post("/videos/{video_id}/visual/reindex", status_code=202)
def reindex_visual(video_id: str, background: BackgroundTasks, db: Session = Depends(get_db)):
    """(Re)build the visual index for an already-processed video."""
    v = get_video_or_404(db, video_id)
    if v.status != "ready":
        raise HTTPException(409, "Video is not ready")
    background.add_task(process_visual, video_id)
    return {"video_id": video_id, "visual_status": "processing"}


@router.get("/videos/{video_id}/file")
def get_file(video_id: str, db: Session = Depends(get_db)):
    v = get_video_or_404(db, video_id)
    return FileResponse(v.stored_path)


@router.get("/videos/{video_id}/transcript")
def get_transcript(video_id: str, db: Session = Depends(get_db)):
    v = get_video_or_404(db, video_id)
    if v.status != "ready":
        raise HTTPException(409, "Transcript not ready")
    segments = storage.read_json(storage.path_for("transcripts", video_id, ".json"))
    chunks = storage.read_json(storage.path_for("indexes", video_id, ".chunks.json"))
    return {"segments": segments, "chunks": chunks}


@router.delete("/videos/{video_id}", status_code=204)
def delete_video(video_id: str, db: Session = Depends(get_db)):
    v = get_video_or_404(db, video_id)
    storage.delete_video_files(video_id)
    db.query(ChatMessage).filter(ChatMessage.video_id == video_id).delete()
    db.delete(v)
    db.commit()
