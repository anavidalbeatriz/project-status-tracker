"""
Transcription model.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class Transcription(Base):
    """Transcription model."""
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    file_path = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    file_type = Column(String, nullable=True)  # audio, video, text
    file_size = Column(Integer, nullable=True)  # in bytes
    raw_text = Column(Text, nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="transcriptions", foreign_keys=[project_id])
    creator = relationship("User", back_populates="transcriptions", foreign_keys=[created_by])
