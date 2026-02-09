"""
Service for generating project health reports.
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from app.db.models.project import Project
from app.db.models.client import Client
from app.db.models.project_status import ProjectStatus
from app.schemas.report import (
    ProjectHealthMetrics,
    ClientHealthSummary,
    OverallHealthMetrics,
    UpcomingDelivery,
    ProjectHealthReport,
    ReportFilters
)
from app.utils.project_status_utils import calculate_project_health_status, get_health_status_label

logger = logging.getLogger(__name__)


def calculate_green_count(is_on_scope: Optional[bool], is_on_time: Optional[bool], is_on_budget: Optional[bool]) -> int:
    """Calculate the number of green (true) statuses."""
    return sum([
        1 if is_on_scope is True else 0,
        1 if is_on_time is True else 0,
        1 if is_on_budget is True else 0
    ])


def get_project_health_metrics(
    db: Session,
    filters: Optional[ReportFilters] = None
) -> List[ProjectHealthMetrics]:
    """Get health metrics for all projects."""
    # Get all projects with their clients
    projects_query = db.query(Project).join(Client, Project.client_id == Client.id)
    
    # Apply client filter
    if filters and filters.client_ids:
        projects_query = projects_query.filter(Project.client_id.in_(filters.client_ids))
    
    projects = projects_query.all()
    metrics = []
    
    for project in projects:
        # Get latest status for this project
        status_query = db.query(ProjectStatus).filter(ProjectStatus.project_id == project.id)
        
        # Apply date filters if provided
        if filters:
            if filters.date_from:
                status_query = status_query.filter(ProjectStatus.updated_at >= filters.date_from)
            if filters.date_to:
                status_query = status_query.filter(ProjectStatus.updated_at <= filters.date_to)
        
        latest_status = status_query.order_by(ProjectStatus.updated_at.desc()).first()
        
        # If no status and filter excludes no-status projects, skip
        if not latest_status:
            if filters and not filters.include_no_status:
                continue
        
        # Calculate health metrics
        is_on_scope = latest_status.is_on_scope if latest_status else None
        is_on_time = latest_status.is_on_time if latest_status else None
        is_on_budget = latest_status.is_on_budget if latest_status else None
        
        green_count = calculate_green_count(is_on_scope, is_on_time, is_on_budget)
        health_status = calculate_project_health_status({
            "is_on_scope": is_on_scope,
            "is_on_time": is_on_time,
            "is_on_budget": is_on_budget
        })
        
        # Apply health status filter
        if filters and filters.health_status:
            if filters.health_status == "green" and health_status != "green":
                continue
            elif filters.health_status == "yellow" and health_status != "yellow":
                continue
            elif filters.health_status == "red" and health_status != "red":
                continue
            elif filters.health_status == "none" and latest_status is not None:
                continue
        
        health_label = get_health_status_label(health_status)
        
        metrics.append(ProjectHealthMetrics(
            project_id=project.id,
            project_name=project.name,
            client_name=project.client.name,
            health_status=health_status,
            health_label=health_label,
            is_on_scope=is_on_scope,
            is_on_time=is_on_time,
            is_on_budget=is_on_budget,
            next_delivery=latest_status.next_delivery if latest_status else None,
            risks=latest_status.risks if latest_status else None,
            last_updated=latest_status.updated_at if latest_status else None,
            green_count=green_count
        ))
    
    return metrics


def calculate_overall_metrics(metrics: List[ProjectHealthMetrics]) -> OverallHealthMetrics:
    """Calculate overall health metrics."""
    total = len(metrics)
    healthy = sum(1 for m in metrics if m.health_status == "green")
    at_risk = sum(1 for m in metrics if m.health_status == "yellow")
    critical = sum(1 for m in metrics if m.health_status == "red")
    no_status = sum(1 for m in metrics if m.last_updated is None)
    
    overall_health = (healthy / total * 100) if total > 0 else 0.0
    
    scope_compliant = sum(1 for m in metrics if m.is_on_scope is True)
    time_compliant = sum(1 for m in metrics if m.is_on_time is True)
    budget_compliant = sum(1 for m in metrics if m.is_on_budget is True)
    
    scope_compliance = (scope_compliant / total * 100) if total > 0 else 0.0
    time_compliance = (time_compliant / total * 100) if total > 0 else 0.0
    budget_compliance = (budget_compliant / total * 100) if total > 0 else 0.0
    
    return OverallHealthMetrics(
        total_projects=total,
        healthy_projects=healthy,
        at_risk_projects=at_risk,
        critical_projects=critical,
        no_status_projects=no_status,
        overall_health_percentage=round(overall_health, 2),
        scope_compliance=round(scope_compliance, 2),
        time_compliance=round(time_compliance, 2),
        budget_compliance=round(budget_compliance, 2)
    )


def get_client_summaries(db: Session, metrics: List[ProjectHealthMetrics]) -> List[ClientHealthSummary]:
    """Get health summaries grouped by client."""
    # Get client IDs for each client name
    client_names = list(set(m.client_name for m in metrics))
    clients = db.query(Client).filter(Client.name.in_(client_names)).all()
    client_id_map = {c.name: c.id for c in clients}
    
    client_data: Dict[str, Dict[str, Any]] = {}
    
    for metric in metrics:
        client_name = metric.client_name
        if client_name not in client_data:
            client_data[client_name] = {
                "client_id": client_id_map.get(client_name, 0),
                "client_name": client_name,
                "total_projects": 0,
                "healthy_projects": 0,
                "at_risk_projects": 0,
                "critical_projects": 0,
                "no_status_projects": 0
            }
        
        client_data[client_name]["total_projects"] += 1
        if metric.health_status == "green":
            client_data[client_name]["healthy_projects"] += 1
        elif metric.health_status == "yellow":
            client_data[client_name]["at_risk_projects"] += 1
        elif metric.health_status == "red":
            client_data[client_name]["critical_projects"] += 1
        if metric.last_updated is None:
            client_data[client_name]["no_status_projects"] += 1
    
    summaries = []
    for client_name, data in client_data.items():
        total = data["total_projects"]
        health_percentage = (data["healthy_projects"] / total * 100) if total > 0 else 0.0
        
        summaries.append(ClientHealthSummary(
            client_id=data["client_id"],
            client_name=client_name,
            total_projects=total,
            healthy_projects=data["healthy_projects"],
            at_risk_projects=data["at_risk_projects"],
            critical_projects=data["critical_projects"],
            no_status_projects=data["no_status_projects"],
            health_percentage=round(health_percentage, 2)
        ))
    
    return sorted(summaries, key=lambda x: x.client_name)


def get_upcoming_deliveries(metrics: List[ProjectHealthMetrics]) -> List[UpcomingDelivery]:
    """Get projects with upcoming deliveries."""
    deliveries = []
    for metric in metrics:
        if metric.next_delivery:
            deliveries.append(UpcomingDelivery(
                project_id=metric.project_id,
                project_name=metric.project_name,
                client_name=metric.client_name,
                next_delivery=metric.next_delivery,
                health_status=metric.health_status,
                last_updated=metric.last_updated or datetime.now()
            ))
    
    # Sort by last updated (most recent first)
    return sorted(deliveries, key=lambda x: x.last_updated, reverse=True)


def generate_project_health_report(
    db: Session,
    filters: Optional[ReportFilters] = None,
    user_name: Optional[str] = None
) -> ProjectHealthReport:
    """Generate a complete project health report."""
    logger.info("Generating project health report")
    
    # Get all project metrics
    project_metrics = get_project_health_metrics(db, filters)
    
    # Calculate overall metrics
    overall_metrics = calculate_overall_metrics(project_metrics)
    
    # Get client summaries
    client_summaries = get_client_summaries(db, project_metrics)
    
    # Get upcoming deliveries
    upcoming_deliveries = get_upcoming_deliveries(project_metrics)
    
    # Get projects at risk and critical
    projects_at_risk = [m for m in project_metrics if m.health_status == "yellow"]
    critical_projects = [m for m in project_metrics if m.health_status == "red"]
    
    return ProjectHealthReport(
        generated_at=datetime.now(),
        generated_by=user_name,
        overall_metrics=overall_metrics,
        project_metrics=project_metrics,
        client_summaries=client_summaries,
        upcoming_deliveries=upcoming_deliveries,
        projects_at_risk=projects_at_risk,
        critical_projects=critical_projects
    )
