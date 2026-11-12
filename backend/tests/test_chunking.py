from app.services.chunking_service import chunk_segments


def seg(s, e, t):
    return {"start": s, "end": e, "text": t}


def test_chunks_preserve_times():
    segs = [seg(0, 5, "a " * 100), seg(5, 10, "b " * 100), seg(10, 15, "c " * 10)]
    chunks = chunk_segments(segs, target_words=150)
    assert chunks[0]["start_seconds"] == 0
    assert chunks[-1]["end_seconds"] == 15


def test_no_merge_across_pause():
    segs = [seg(0, 5, "hello there"), seg(100, 105, "different topic")]
    chunks = chunk_segments(segs, max_gap=8)
    assert len(chunks) == 2
    assert chunks[1]["start_seconds"] == 100
