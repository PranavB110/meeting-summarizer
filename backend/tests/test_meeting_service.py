"""
Tests for the meeting processing pipeline.

ASR and LLM providers are mocked here — we're testing the orchestration
logic (status transitions, data persistence), not the real transcription
or summarization APIs, which are already verified manually against real
audio and the live Groq API.
"""
from unittest.mock import patch

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.meeting import Meeting, MeetingStatus
from app.providers.asr.base import TranscriptionResult
from app.providers.llm.base import SummaryResult
from app.services.meeting_service import process_meeting


def _make_meeting(db):
    meeting = Meeting(
        original_filename="test.wav",
        audio_path="/fake/path/test.wav",
        status=MeetingStatus.UPLOADED,
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting


def test_process_meeting_success_path():
    db = SessionLocal()
    meeting = _make_meeting(db)
    settings = get_settings()

    fake_transcript = TranscriptionResult(text="We decided to ship on Friday.", language="en")
    fake_summary = SummaryResult(
        summary="Team agreed on Friday ship date.",
        key_decisions=["Ship on Friday"],
        action_items=["Owner: prepare release notes"],
    )

    with patch("app.services.meeting_service.get_asr_provider") as mock_asr, \
         patch("app.services.meeting_service.get_llm_provider") as mock_llm:
        mock_asr.return_value.transcribe.return_value = fake_transcript
        mock_llm.return_value.summarize.return_value = fake_summary

        process_meeting(meeting.id, db, settings)

    db.refresh(meeting)
    assert meeting.status == MeetingStatus.COMPLETED
    assert meeting.transcript == "We decided to ship on Friday."
    assert meeting.summary == "Team agreed on Friday ship date."
    assert "Ship on Friday" in meeting.key_decisions
    assert meeting.error_message is None
    db.close()


def test_process_meeting_marks_failed_on_asr_error():
    db = SessionLocal()
    meeting = _make_meeting(db)
    settings = get_settings()

    with patch("app.services.meeting_service.get_asr_provider") as mock_asr:
        mock_asr.return_value.transcribe.side_effect = RuntimeError("ASR blew up")

        process_meeting(meeting.id, db, settings)

    db.refresh(meeting)
    assert meeting.status == MeetingStatus.FAILED
    assert "ASR blew up" in meeting.error_message
    db.close()


def test_process_meeting_marks_failed_on_llm_error():
    db = SessionLocal()
    meeting = _make_meeting(db)
    settings = get_settings()

    fake_transcript = TranscriptionResult(text="Some transcript.", language="en")

    with patch("app.services.meeting_service.get_asr_provider") as mock_asr, \
         patch("app.services.meeting_service.get_llm_provider") as mock_llm:
        mock_asr.return_value.transcribe.return_value = fake_transcript
        mock_llm.return_value.summarize.side_effect = RuntimeError("LLM blew up")

        process_meeting(meeting.id, db, settings)

    db.refresh(meeting)
    assert meeting.status == MeetingStatus.FAILED
    assert "LLM blew up" in meeting.error_message
    assert meeting.transcript == "Some transcript."  # transcript was saved before the LLM failed
    db.close()