from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from app.models.voice_note import TranscriptionStatus


class VoiceNoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class VoiceNoteCreate(VoiceNoteBase):
    pass


class VoiceNoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class VoiceNoteResponse(VoiceNoteBase):
    id: int
    file_name: str
    file_size: int
    mime_type: str
    duration: Optional[float]
    transcription_text: Optional[str]
    transcription_status: TranscriptionStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class VoiceNoteList(BaseModel):
    items: list[VoiceNoteResponse]
    total: int
    page: int
    per_page: int
    pages: int


class TranscriptionResponse(BaseModel):
    id: int
    transcription_text: Optional[str]
    transcription_status: TranscriptionStatus
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True