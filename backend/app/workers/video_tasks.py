import logging

from app.db.models import Video
from app.db.session import SessionLocal
from app.services import (chunking_service, embedding_service, media_service,
                          storage_service as storage, transcription_service,
                          vector_store_service)

log = logging.getLogger("vidscope.worker")


def _update(db, video, **fields):
    for k, v in fields.items():
        setattr(video, k, v)
    db.commit()


def process_video(video_id: str) -> None:
    db = SessionLocal()
    video = db.get(Video, video_id)
    if video is None:
        db.close()
        return
    try:
        from pathlib import Path

        src = Path(video.stored_path)
        _update(db, video, status="processing", processing_stage="probing", progress=5)
        duration = media_service.probe_duration(src)
        _update(db, video, duration_seconds=duration)

        _update(db, video, processing_stage="extracting_audio", progress=15)
        wav = storage.path_for("audio", video_id, ".wav")
        media_service.extract_audio(src, wav)

        _update(db, video, processing_stage="transcribing", progress=35)
        segments = transcription_service.transcribe(wav)
        if not segments:
            raise media_service.MediaError("no_speech_detected")
        storage.write_json(storage.path_for("transcripts", video_id, ".json"), segments)

        _update(db, video, processing_stage="indexing", progress=80)
        chunks = chunking_service.chunk_segments(segments)
        vectors = embedding_service.embed([c["text"] for c in chunks])
        vector_store_service.build_index(video_id, chunks, vectors)

        # Only ready once transcript AND index are saved.
        _update(db, video, status="ready", processing_stage="done", progress=100, visual_status="processing")
    except media_service.MediaError as e:
        log.warning("video %s failed: %s", video_id, e.code)
        _update(db, video, status="failed", error_code=e.code)
        return
    except Exception:
        log.exception("video %s failed unexpectedly", video_id)
        _update(db, video, status="failed", error_code="processing_error")
        return
    finally:
        db.close()

    # Visual indexing is a separate stage: transcript Q&A is already usable.
    process_visual(video_id)


def process_visual(video_id: str) -> None:
    """Extract frames, embed with CLIP, build the visual FAISS index.

    Never changes the video's transcript `status`; failures only set `visual_status`.
    """
    from pathlib import Path

    from app.services import frame_service, visual_retrieval_service

    db = SessionLocal()
    video = db.get(Video, video_id)
    if video is None:
        db.close()
        return
    try:
        _update(db, video, visual_status="processing")
        frames = frame_service.extract_frames(Path(video.stored_path), storage.path_for("frames", video_id, ""))
        visual_retrieval_service.build_index(video_id, frames)
        _update(db, video, visual_status="ready")
    except frame_service.FrameError as e:
        log.warning("visual index for %s failed: %s", video_id, e.code)
        _update(db, video, visual_status="failed")
    except Exception:
        log.exception("visual index for %s failed unexpectedly", video_id)
        _update(db, video, visual_status="failed")
    finally:
        db.close()
