"""
Project model.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Project(Base):
    """Project model."""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="created_projects", foreign_keys=[created_by])
    client = relationship("Client", back_populates="projects", foreign_keys=[client_id])
    statuses = relationship("ProjectStatus", back_populates="project", cascade="all, delete-orphan")
    transcriptions = relationship("Transcription", back_populates="project", cascade="all, delete-orphan")
