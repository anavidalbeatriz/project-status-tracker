"""
User model.
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.database import Base


class UserRole(str, enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    TECH_LEAD = "tech_lead"
    USER = "user"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(Enum(UserRole, native_enum=False, length=20, values_callable=lambda x: [e.value for e in x]), default=UserRole.USER, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    created_projects = relationship("Project", back_populates="creator", foreign_keys="Project.created_by")
    updated_statuses = relationship("ProjectStatus", back_populates="updater", foreign_keys="ProjectStatus.updated_by")
    transcriptions = relationship("Transcription", back_populates="creator", foreign_keys="Transcription.created_by")
