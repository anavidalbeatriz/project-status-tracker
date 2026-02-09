"""
Transcription schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.user import UserResponse
from app.schemas.project import ProjectResponse


class TranscriptionBase(BaseModel):
    """Base transcription schema."""
    project_id: int


class TranscriptionCreate(TranscriptionBase):
    """Transcription creation schema."""
    pass


class TranscriptionResponse(TranscriptionBase):
    """Transcription response schema."""
    id: int
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    raw_text: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class TranscriptionDetailResponse(TranscriptionResponse):
    """Transcription detail response with related data."""
    project: Optional[ProjectResponse] = None
    creator: Optional[UserResponse] = None

    class Config:
        from_attributes = True
