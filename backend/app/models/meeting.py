"""ORM model representing a single meeting processing job."""
import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, DateTime, Enum
from app.db.session import Base


class MeetingStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    TRANSCRIBING = "transcribing"
    TRANSCRIBED = "transcribed"
    SUMMARIZING = "summarizing"
    COMPLETED = "completed"
    FAILED = "failed"


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String, primary_key=True, default=_uuid)
    original_filename = Column(String, nullable=False)
    audio_path = Column(String, nullable=False)

    status = Column(Enum(MeetingStatus), default=MeetingStatus.UPLOADED, nullable=False)
    error_message = Column(Text, nullable=True)

    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    action_items = Column(Text, nullable=True)   # JSON-encoded list
    key_decisions = Column(Text, nullable=True)  # JSON-encoded list

    asr_engine_used = Column(String, nullable=True)
    llm_provider_used = Column(String, nullable=True)

    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)