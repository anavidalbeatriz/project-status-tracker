"""Pydantic schemas for request/response validation."""
# Import all schemas to ensure they're loaded
from app.schemas import client, project, user, project_status, auth

# Resolve forward references after all modules are loaded
client._resolve_forward_refs()
project._resolve_forward_refs()
