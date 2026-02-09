"""
Project Status management endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc

from app.db.database import get_db
from app.db.models.project_status import ProjectStatus
from app.db.models.project import Project
from app.db.models.user import User
from app.schemas.project_status import (
    ProjectStatusCreate,
    ProjectStatusUpdate,
    ProjectStatusResponse,
    ProjectStatusDetailResponse
)
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[ProjectStatusResponse])
async def get_project_statuses(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all project statuses, optionally filtered by project."""
    query = db.query(ProjectStatus)
    
    if project_id is not None:
        query = query.filter(ProjectStatus.project_id == project_id)
    
    # Order by most recent first
    query = query.order_by(desc(ProjectStatus.updated_at))
    
    statuses = query.offset(skip).limit(limit).all()
    return statuses


@router.get("/{status_id}", response_model=ProjectStatusDetailResponse)
async def get_project_status(
    status_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific project status by ID."""
    project_status = (
        db.query(ProjectStatus)
        .options(joinedload(ProjectStatus.updater))
        .filter(ProjectStatus.id == status_id)
        .first()
    )
    
    if project_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project status not found"
        )
    
    return project_status


@router.get("/project/{project_id}/latest", response_model=Optional[ProjectStatusDetailResponse])
async def get_latest_project_status(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the latest project status for a project."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project_status = (
        db.query(ProjectStatus)
        .options(joinedload(ProjectStatus.updater))
        .filter(ProjectStatus.project_id == project_id)
        .order_by(desc(ProjectStatus.updated_at))
        .first()
    )
    
    return project_status


@router.post("/", response_model=ProjectStatusResponse, status_code=status.HTTP_201_CREATED)
async def create_project_status(
    status_data: ProjectStatusCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new project status."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == status_data.project_id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    db_status = ProjectStatus(
        project_id=status_data.project_id,
        is_on_scope=status_data.is_on_scope,
        is_on_time=status_data.is_on_time,
        is_on_budget=status_data.is_on_budget,
        next_delivery=status_data.next_delivery,
        risks=status_data.risks,
        updated_by=current_user.id
    )
    
    db.add(db_status)
    db.commit()
    db.refresh(db_status)
    
    return db_status


@router.put("/{status_id}", response_model=ProjectStatusResponse)
async def update_project_status(
    status_id: int,
    status_data: ProjectStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a project status."""
    project_status = db.query(ProjectStatus).filter(ProjectStatus.id == status_id).first()
    if project_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project status not found"
        )
    
    # Update fields
    update_data = status_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project_status, field, value)
    
    # Update the updated_by field to current user
    project_status.updated_by = current_user.id
    
    db.commit()
    db.refresh(project_status)
    
    return project_status


@router.delete("/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project_status(
    status_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a project status."""
    project_status = db.query(ProjectStatus).filter(ProjectStatus.id == status_id).first()
    if project_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project status not found"
        )
    
    db.delete(project_status)
    db.commit()
    
    return None
