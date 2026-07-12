"""
Orchestrates the full meeting-processing pipeline:
audio file -> transcription -> summarization -> persisted result.

Kept separate from the API layer so the pipeline logic is testable and
reusable independent of HTTP/FastAPI concerns.
"""
import json
import shutil
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.meeting import Meeting, MeetingStatus
from app.providers.asr.factory import get_asr_provider
from app.providers.llm.factory import get_llm_provider


def save_uploaded_audio(upload_file, settings: Settings) -> tuple[str, str]:
    """Saves an uploaded file to disk with a unique name. Returns (path, original_filename)."""
    original_filename = upload_file.filename or "unknown_audio"
    extension = Path(original_filename).suffix or ".audio"
    unique_name = f"{uuid.uuid4()}{extension}"
    destination = Path(settings.audio_storage_dir) / unique_name

    with open(destination, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return str(destination), original_filename


def create_meeting_record(db: Session, audio_path: str, original_filename: str) -> Meeting:
    meeting = Meeting(
        original_filename=original_filename,
        audio_path=audio_path,
        status=MeetingStatus.UPLOADED,
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


def process_meeting(meeting_id: str, db: Session, settings: Settings) -> None:
    """
    Runs the full pipeline for a single meeting: transcribe, then summarize.
    Designed to run as a background task after the upload response is sent,
    so the client doesn't have to wait for processing to finish.
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if meeting is None:
        return

    try:
        # --- Transcription ---
        meeting.status = MeetingStatus.TRANSCRIBING
        db.commit()

        asr_provider = get_asr_provider(settings)
        transcription = asr_provider.transcribe(meeting.audio_path, language="en")

        meeting.transcript = transcription.text
        meeting.asr_engine_used = settings.asr_engine
        meeting.status = MeetingStatus.TRANSCRIBED
        db.commit()

        # --- Summarization ---
        meeting.status = MeetingStatus.SUMMARIZING
        db.commit()

        llm_provider = get_llm_provider(settings)
        summary_result = llm_provider.summarize(transcription.text)

        meeting.summary = summary_result.summary
        meeting.key_decisions = json.dumps(summary_result.key_decisions)
        meeting.action_items = json.dumps(summary_result.action_items)
        meeting.llm_provider_used = settings.llm_provider
        meeting.status = MeetingStatus.COMPLETED
        db.commit()

    except Exception as exc:
        meeting.status = MeetingStatus.FAILED
        meeting.error_message = str(exc)
        db.commit()