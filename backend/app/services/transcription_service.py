from functools import lru_cache
from pathlib import Path

from app.core.config import settings


@lru_cache(maxsize=1)
def _model():
    from faster_whisper import WhisperModel

    return WhisperModel(
        settings.asr_model_size,
        device=settings.asr_device,
        compute_type=settings.asr_compute_type if settings.asr_compute_type != "auto" else "default",
    )


def transcribe(audio: Path) -> list[dict]:
    segments, _info = _model().transcribe(str(audio), vad_filter=True)
    return [
        {"start": float(s.start), "end": float(s.end), "text": s.text.strip()}
        for s in segments
        if s.text.strip()
    ]
