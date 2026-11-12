import numpy as np
import pytest

from app.services import frame_service
from app.services.visual_retrieval_service import has_visual_intent, parse_timecodes


def test_parse_timecodes():
    assert parse_timecodes("What does the slide at 12:30 explain?") == [750]
    assert parse_timecodes("at 1:02:03 and 00:05") == [3723, 5]
    assert parse_timecodes("ratio of 3:99 is odd") == []
    assert parse_timecodes("no times here") == []


def test_visual_intent():
    assert has_visual_intent("Find the frame showing the database schema")
    assert has_visual_intent("What architecture diagram does the instructor draw?")
    assert not has_visual_intent("What is the capital of France?")


def _make_video(path, scenes, fps=10, seconds_per_scene=6):
    cv2 = pytest.importorskip("cv2")
    w = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (160, 90))
    if not w.isOpened():
        pytest.skip("no mp4v encoder")
    for color in scenes:
        frame = np.full((90, 160, 3), color, dtype="uint8")
        for _ in range(fps * seconds_per_scene):
            w.write(frame)
    w.release()


def test_extract_frames_keeps_scene_changes_only(tmp_path):
    video = tmp_path / "v.mp4"
    _make_video(video, scenes=[20, 220, 20])  # 3 scenes x 6s
    frames = frame_service.extract_frames(video, tmp_path / "frames")
    times = [f["timestamp"] for f in frames]
    assert times == sorted(times)
    assert 3 <= len(frames) <= 4          # one per scene, not one per 2s sample (9)
    assert (tmp_path / "frames" / "frame-0001.jpg").is_file()


def test_unreadable_video(tmp_path):
    bad = tmp_path / "bad.mp4"
    bad.write_bytes(b"not a video")
    with pytest.raises(frame_service.FrameError):
        frame_service.extract_frames(bad, tmp_path / "frames")
