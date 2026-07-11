"""Pydantic schemas — the API's public contract, decoupled from the ORM model."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class MeetingCreatedResponse(BaseModel):
    id: str
    status: str
    original_filename: str


class MeetingDetailResponse(BaseModel):
    id: str
    original_filename: str
    status: str
    error_message: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    action_items: Optional[List[str]] = None
    key_decisions: Optional[List[str]] = None
    asr_engine_used: Optional[str] = None
    llm_provider_used: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MeetingListItem(BaseModel):
    id: str
    original_filename: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}