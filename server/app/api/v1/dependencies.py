"""
Shared dependencies for API endpoints.
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models.user import User
from app.api.v1.endpoints.auth import get_current_user

# Re-export get_current_user for easy importing
__all__ = ["get_current_user", "get_db"]
