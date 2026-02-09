"""
Client schemas.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class ClientBase(BaseModel):
    """Base client schema."""
    name: str


class ClientCreate(ClientBase):
    """Client creation schema."""
    pass


class ClientUpdate(BaseModel):
    """Client update schema."""
    name: Optional[str] = None


class ClientResponse(ClientBase):
    """Client response schema."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClientDetailResponse(ClientResponse):
    """Client response schema with projects."""
    projects: List["ProjectResponse"] = []

    class Config:
        from_attributes = True


# Resolve forward references after all imports are complete
def _resolve_forward_refs():
    """Resolve forward references for ClientDetailResponse."""
    from app.schemas.project import ProjectResponse
    ClientDetailResponse.model_rebuild()
