"""
Project schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

from app.schemas.user import UserResponse
from app.schemas.client import ClientResponse


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str
    client_id: int


class ProjectCreate(ProjectBase):
    """Project creation schema."""
    pass


class ProjectUpdate(BaseModel):
    """Project update schema."""
    name: Optional[str] = None
    client_id: Optional[int] = None


class ProjectResponse(ProjectBase):
    """Project response schema."""
    id: int
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    client: Optional["ClientResponse"] = None

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    """Project detail response with creator and client information."""
    creator: Optional[UserResponse] = None
    client: Optional["ClientResponse"] = None

    class Config:
        from_attributes = True


# Resolve forward references after all imports are complete
def _resolve_forward_refs():
    """Resolve forward references for ProjectDetailResponse and ProjectResponse."""
    from app.schemas.client import ClientResponse
    ProjectResponse.model_rebuild()
    ProjectDetailResponse.model_rebuild()
