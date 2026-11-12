from datetime import datetime, timezone

from sqlalchemy import Float, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


def _now():
    return datetime.now(timezone.utc)


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    original_filename: Mapped[str] = mapped_column(String)
    stored_path: Mapped[str] = mapped_column(String)
    content_type: Mapped[str] = mapped_column(String, default="")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String, default="queued")
    processing_stage: Mapped[str | None] = mapped_column(String, nullable=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    # Separate from `status`: visual indexing never blocks or fails transcript Q&A.
    # pending | processing | ready | failed
    visual_status: Mapped[str] = mapped_column(String, default="pending", server_default="pending")
    error_code: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    video_id: Mapped[str] = mapped_column(String, index=True)
    conversation_id: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
