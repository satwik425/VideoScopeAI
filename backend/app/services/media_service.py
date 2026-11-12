import json
import subprocess
from pathlib import Path


class MediaError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def probe_duration(path: Path) -> float:
    """Verify the file is real media via ffprobe and return its duration."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type",
             "-of", "json", str(path)],
            capture_output=True, text=True, timeout=60, check=True,
        )
    except FileNotFoundError:
        raise MediaError("ffmpeg_not_installed")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        raise MediaError("invalid_media")
    info = json.loads(out.stdout or "{}")
    if not any(s.get("codec_type") == "audio" for s in info.get("streams", [])):
        raise MediaError("no_audio_stream")
    try:
        return float(info["format"]["duration"])
    except (KeyError, ValueError):
        raise MediaError("invalid_media")


def extract_audio(video: Path, out_wav: Path) -> None:
    """Extract mono 16 kHz WAV audio."""
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", str(out_wav)],
            capture_output=True, timeout=3600, check=True,
        )
    except FileNotFoundError:
        raise MediaError("ffmpeg_not_installed")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        raise MediaError("audio_extraction_failed")
