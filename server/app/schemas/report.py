"""
Report schemas for project health reports.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.schemas.project import ProjectResponse
from app.schemas.client import ClientResponse


class ProjectHealthMetrics(BaseModel):
    """Health metrics for a single project."""
    project_id: int
    project_name: str
    client_name: str
    health_status: str  # "green", "yellow", "red"
    health_label: str  # "Healthy", "At Risk", "Critical"
    is_on_scope: Optional[bool] = None
    is_on_time: Optional[bool] = None
    is_on_budget: Optional[bool] = None
    next_delivery: Optional[str] = None
    risks: Optional[str] = None
    last_updated: Optional[datetime] = None
    green_count: int  # Number of green statuses (0-3)


class ClientHealthSummary(BaseModel):
    """Health summary for a client."""
    client_id: int
    client_name: str
    total_projects: int
    healthy_projects: int
    at_risk_projects: int
    critical_projects: int
    no_status_projects: int
    health_percentage: float  # Percentage of healthy projects


class OverallHealthMetrics(BaseModel):
    """Overall health metrics across all projects."""
    total_projects: int
    healthy_projects: int
    at_risk_projects: int
    critical_projects: int
    no_status_projects: int
    overall_health_percentage: float
    scope_compliance: float  # Percentage of projects on scope
    time_compliance: float  # Percentage of projects on time
    budget_compliance: float  # Percentage of projects on budget


class UpcomingDelivery(BaseModel):
    """Upcoming delivery information."""
    project_id: int
    project_name: str
    client_name: str
    next_delivery: str
    health_status: str
    last_updated: datetime


class ProjectHealthReport(BaseModel):
    """Complete project health report."""
    generated_at: datetime
    generated_by: Optional[str] = None
    overall_metrics: OverallHealthMetrics
    project_metrics: List[ProjectHealthMetrics]
    client_summaries: List[ClientHealthSummary]
    upcoming_deliveries: List[UpcomingDelivery]
    projects_at_risk: List[ProjectHealthMetrics]
    critical_projects: List[ProjectHealthMetrics]
    
    class Config:
        from_attributes = True


class ReportFilters(BaseModel):
    """Filters for report generation."""
    client_ids: Optional[List[int]] = None
    health_status: Optional[str] = None  # "green", "yellow", "red", "none"
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    include_no_status: bool = True
