import json
import shutil
from pathlib import Path

from app.core.config import settings

SUBDIRS = ("originals", "audio", "transcripts", "indexes", "frames")


def init_storage() -> None:
    for d in SUBDIRS:
        (settings.storage_path / d).mkdir(parents=True, exist_ok=True)


def path_for(kind: str, video_id: str, suffix: str) -> Path:
    """Server-controlled path built only from a UUID, never user input."""
    return settings.storage_path / kind / f"{video_id}{suffix}"


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def delete_video_files(video_id: str) -> None:
    for d in SUBDIRS:
        for p in (settings.storage_path / d).glob(f"{video_id}*"):
            if p.is_dir():
                shutil.rmtree(p, ignore_errors=True)
            else:
                p.unlink(missing_ok=True)
