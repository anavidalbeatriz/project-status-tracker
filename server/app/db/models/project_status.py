"""
Project Status model.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ProjectStatus(Base):
    """Project Status model."""
    __tablename__ = "project_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    is_on_scope = Column(Boolean, nullable=True)
    is_on_time = Column(Boolean, nullable=True)
    is_on_budget = Column(Boolean, nullable=True)
    next_delivery = Column(Text, nullable=True)
    risks = Column(Text, nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="statuses", foreign_keys=[project_id])
    updater = relationship("User", back_populates="updated_statuses", foreign_keys=[updated_by])
