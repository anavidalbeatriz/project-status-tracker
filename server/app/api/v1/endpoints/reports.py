"""
Report generation endpoints.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.database import get_db
from app.db.models.user import User
from app.schemas.report import ProjectHealthReport, ReportFilters
from app.api.v1.endpoints.auth import get_current_user
from app.services.report_service import generate_project_health_report

router = APIRouter()


@router.get("/health", response_model=ProjectHealthReport)
async def get_project_health_report(
    client_ids: Optional[List[int]] = Query(None, description="Filter by client IDs"),
    health_status: Optional[str] = Query(None, description="Filter by health status (green, yellow, red, none)"),
    date_from: Optional[datetime] = Query(None, description="Filter by date from"),
    date_to: Optional[datetime] = Query(None, description="Filter by date to"),
    include_no_status: bool = Query(True, description="Include projects with no status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a project health report with optional filters."""
    filters = ReportFilters(
        client_ids=client_ids,
        health_status=health_status,
        date_from=date_from,
        date_to=date_to,
        include_no_status=include_no_status
    )
    
    try:
        report = generate_project_health_report(
            db=db,
            filters=filters,
            user_name=current_user.name
        )
        return report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )
