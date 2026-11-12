"""Representative frame extraction with OpenCV.

Samples candidate frames at a fixed interval, keeps a frame only when the picture
changed meaningfully (slide change, new diagram, etc.) or when too long has passed.
"""
from pathlib import Path

from app.core.config import settings


class FrameError(Exception):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def _signature(frame):
    import cv2

    return cv2.resize(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (64, 36)).astype("float32")


def extract_frames(video_path: Path, out_dir: Path) -> list[dict]:
    """Save JPEG frames to out_dir; return [{"id", "timestamp"}] in time order."""
    import cv2
    import numpy as np

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise FrameError("video_unreadable")
    try:
        fps = cap.get(cv2.CAP_PROP_FPS) or 0
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if fps <= 0 or total <= 0:
            raise FrameError("video_unreadable")

        step = max(1, int(round(fps * settings.frame_sample_interval)))
        kept: list[tuple[float, "np.ndarray"]] = []  # (timestamp, frame)
        last_sig, last_t = None, -1e9

        for idx in range(0, total, step):
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if not ok:
                continue
            t = idx / fps
            sig = _signature(frame)
            changed = last_sig is None or float(np.abs(sig - last_sig).mean()) > settings.frame_change_threshold
            if changed or t - last_t >= settings.frame_max_gap:
                kept.append((t, frame))
                last_sig, last_t = sig, t

        if not kept:
            raise FrameError("no_frames")

        # Cap the count by uniform subsampling.
        if len(kept) > settings.frame_max_count:
            pick = np.linspace(0, len(kept) - 1, settings.frame_max_count).astype(int)
            kept = [kept[i] for i in pick]

        out_dir.mkdir(parents=True, exist_ok=True)
        frames = []
        for n, (t, frame) in enumerate(kept, start=1):
            h, w = frame.shape[:2]
            if w > 640:
                frame = cv2.resize(frame, (640, int(h * 640 / w)))
            fid = f"frame-{n:04d}"
            cv2.imwrite(str(out_dir / f"{fid}.jpg"), frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            frames.append({"id": fid, "timestamp": round(t, 2)})
        return frames
    finally:
        cap.release()
