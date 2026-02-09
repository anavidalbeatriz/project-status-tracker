"""
Project Status schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.schemas.user import UserResponse


class ProjectStatusBase(BaseModel):
    """Base project status schema."""
    is_on_scope: Optional[bool] = None
    is_on_time: Optional[bool] = None
    is_on_budget: Optional[bool] = None
    next_delivery: Optional[str] = None
    risks: Optional[str] = None


class ProjectStatusCreate(ProjectStatusBase):
    """Project status creation schema."""
    project_id: int


class ProjectStatusUpdate(ProjectStatusBase):
    """Project status update schema."""
    pass


class ProjectStatusResponse(ProjectStatusBase):
    """Project status response schema."""
    id: int
    project_id: int
    updated_by: int
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectStatusDetailResponse(ProjectStatusResponse):
    """Project status detail response with updater information."""
    updater: Optional[UserResponse] = None

    class Config:
        from_attributes = True
