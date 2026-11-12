def _words(text: str) -> int:
    return len(text.split())


def chunk_segments(
    segments: list[dict],
    target_words: int = 180,
    max_gap: float = 8.0,
    overlap_segments: int = 1,
) -> list[dict]:
    """Merge adjacent ASR segments into timestamped chunks.

    Never merges across a pause longer than `max_gap` seconds.
    Roughly 180 words ~ 250 tokens.
    """
    chunks: list[dict] = []
    cur: list[dict] = []

    def flush():
        if not cur:
            return
        chunks.append({
            "id": f"chunk-{len(chunks):03d}",
            "start_seconds": cur[0]["start"],
            "end_seconds": cur[-1]["end"],
            "text": " ".join(s["text"] for s in cur),
        })

    for seg in segments:
        if cur and seg["start"] - cur[-1]["end"] > max_gap:
            flush()
            cur = []
        cur.append(seg)
        if sum(_words(s["text"]) for s in cur) >= target_words:
            flush()
            cur = cur[-overlap_segments:] if overlap_segments else []
    if cur and (not chunks or cur[-1]["end"] > chunks[-1]["end_seconds"]):
        flush()
    return chunks
