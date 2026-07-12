"""API routes for uploading and retrieving meeting summaries."""
import json

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.meeting import Meeting
from app.schemas.meeting import MeetingCreatedResponse, MeetingDetailResponse, MeetingListItem
from app.services.meeting_service import (
    create_meeting_record,
    process_meeting,
    save_uploaded_audio,
)

router = APIRouter(prefix="/meetings", tags=["meetings"])

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".webm", ".ogg"}


@router.post("", response_model=MeetingCreatedResponse, status_code=201)
def upload_meeting(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload a meeting audio file. Processing (transcription + summarization)
    runs in the background — poll GET /meetings/{id} for status/results.
    """
    settings = get_settings()

    filename = file.filename or ""
    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'. Allowed: {sorted(ALLOWED_EXTENSIONS)}",
        )

    audio_path, original_filename = save_uploaded_audio(file, settings)
    meeting = create_meeting_record(db, audio_path, original_filename)

    background_tasks.add_task(process_meeting, meeting.id, db, settings)

    return MeetingCreatedResponse(
        id=meeting.id,
        status=meeting.status.value,
        original_filename=meeting.original_filename,
    )


@router.get("/{meeting_id}", response_model=MeetingDetailResponse)
def get_meeting(meeting_id: str, db: Session = Depends(get_db)):
    """Poll this endpoint to check processing status and retrieve results."""
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return MeetingDetailResponse(
        id=meeting.id,
        original_filename=meeting.original_filename,
        status=meeting.status.value,
        error_message=meeting.error_message,
        transcript=meeting.transcript,
        summary=meeting.summary,
        action_items=json.loads(meeting.action_items) if meeting.action_items else None,
        key_decisions=json.loads(meeting.key_decisions) if meeting.key_decisions else None,
        asr_engine_used=meeting.asr_engine_used,
        llm_provider_used=meeting.llm_provider_used,
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
    )


@router.get("", response_model=list[MeetingListItem])
def list_meetings(db: Session = Depends(get_db)):
    """List all meetings, most recent first."""
    meetings = db.query(Meeting).order_by(Meeting.created_at.desc()).all()
    return meetings