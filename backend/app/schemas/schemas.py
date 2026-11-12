from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    video_id: str
    filename: str
    status: str


class VideoOut(BaseModel):
    video_id: str
    filename: str
    content_type: str
    size_bytes: int
    duration_seconds: float | None
    status: str
    stage: str | None
    error_code: str | None


class StatusOut(BaseModel):
    video_id: str
    status: str
    stage: str | None
    progress: int
    error_code: str | None
    visual_status: str = "pending"


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    conversation_id: str | None = None


class Evidence(BaseModel):
    chunk_id: str
    start_seconds: float
    end_seconds: float
    text: str


class FrameEvidence(BaseModel):
    frame_id: str
    timestamp_seconds: float
    score: float
    match: str  # "semantic" (CLIP similarity) or "timestamp" (user named a time)
    nearby_text: str = ""


class ChatResponse(BaseModel):
    answer: str
    status: str
    evidence: list[Evidence]
    visual_evidence: list[FrameEvidence] = []
