import base64
from pathlib import Path

import httpx

from app.core.config import settings
from app.utils.timecodes import format_timecode

SYSTEM_PROMPT = (
    "You answer questions about a video using ONLY the evidence provided: spoken transcript excerpts "
    "and retrieved video frames (including their attached images and surrounding speech). "
    "Do not use outside knowledge. If the evidence does not contain enough information, say so plainly. "
    "Be concise and direct. Inspect any attached frame images carefully for on-screen text, slides, "
    "diagrams, colors, and visual changes, and combine those visual details with the spoken transcript. "
    "Cite supporting moments as [mm:ss] using only the timestamps shown; never invent timestamps. "
    "Distinguish what is directly shown or stated in the video from what you infer."
)

# Providers expose OpenAI-compatible chat completions APIs.
BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "xai": "https://api.x.ai/v1",
    "groq": "https://api.groq.com/openai/v1",
}


class LLMError(Exception):
    pass


def build_messages(question: str, evidence: list[dict], history: list[dict],
                   frames: list[dict] | None = None, include_images: bool = True) -> list[dict]:
    parts = []
    if evidence:
        parts.append("Transcript excerpts:\n" + "\n\n".join(
            f"[{format_timecode(e['start_seconds'])}-{format_timecode(e['end_seconds'])}] {e['text']}"
            for e in evidence))
    if frames:
        lines = []
        for f in frames:
            how = "named by the user" if f.get("match") == "timestamp" else "visually similar to the question"
            speech = f.get("nearby_text") or "(no speech near this frame)"
            lines.append(f"[Frame at {format_timecode(f['timestamp'])}] retrieved ({how}). Speech around it: {speech}")
        parts.append("Retrieved video frames:\n" + "\n".join(lines))

    prompt_text = "\n\n".join(parts) + f"\n\nQuestion: {question}"
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    msgs += history[-6:]

    image_blocks = []
    if include_images and frames:
        for f in frames:
            img_path: Path | None = f.get("image_path")
            if img_path and Path(img_path).is_file():
                b64 = base64.b64encode(Path(img_path).read_bytes()).decode("ascii")
                image_blocks.append({"type": "text", "text": f"Attached image for [Frame at {format_timecode(f['timestamp'])}]:"})
                image_blocks.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}})

    if image_blocks:
        user_content: str | list[dict] = [{"type": "text", "text": prompt_text}, *image_blocks]
    else:
        user_content = prompt_text

    msgs.append({"role": "user", "content": user_content})
    return msgs


def generate_answer(question: str, evidence: list[dict], history: list[dict] | None = None,
                    frames: list[dict] | None = None) -> str:
    base_url = BASE_URLS.get(settings.llm_provider)
    if base_url is None:
        raise LLMError("unsupported_provider")
    if not settings.llm_api_key:
        raise LLMError("llm_not_configured")
    try:
        r = httpx.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {settings.llm_api_key}"},
            json={
                "model": settings.llm_model,
                "messages": build_messages(question, evidence, history or [], frames, include_images=True),
                "temperature": 0.2,
            },
            timeout=60,
        )
        # Fallback if a text-only model rejects image_url blocks with 400
        if r.status_code == 400 and frames:
            r = httpx.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.llm_api_key}"},
                json={
                    "model": settings.llm_model,
                    "messages": build_messages(question, evidence, history or [], frames, include_images=False),
                    "temperature": 0.2,
                },
                timeout=60,
            )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except (httpx.HTTPError, KeyError, IndexError):
        raise LLMError("llm_request_failed")
