"""
API v1 router.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, projects, clients, transcriptions, project_status, reports

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(transcriptions.router, prefix="/transcriptions", tags=["transcriptions"])
api_router.include_router(project_status.router, prefix="/project-status", tags=["project-status"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])


@api_router.get("/")
async def api_root():
    """API root endpoint."""
    return {"message": "API v1", "version": "1.0.0"}
