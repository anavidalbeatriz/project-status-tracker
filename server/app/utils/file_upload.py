"""
File upload utilities.
"""
import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException, status

from app.core.config import settings
from app.services.sharepoint_service import (
    upload_file_to_sharepoint,
    download_file_from_sharepoint,
    delete_file_from_sharepoint
)


ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".webm"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm", ".flv"}
ALLOWED_TEXT_EXTENSIONS = {".txt", ".doc", ".docx", ".pdf"}

ALLOWED_EXTENSIONS = ALLOWED_AUDIO_EXTENSIONS | ALLOWED_VIDEO_EXTENSIONS | ALLOWED_TEXT_EXTENSIONS


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return Path(filename).suffix.lower()


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS


def get_file_type(filename: str) -> str:
    """Determine file type based on extension."""
    ext = get_file_extension(filename)
    if ext in ALLOWED_AUDIO_EXTENSIONS:
        return "audio"
    elif ext in ALLOWED_VIDEO_EXTENSIONS:
        return "video"
    elif ext in ALLOWED_TEXT_EXTENSIONS:
        return "text"
    return "unknown"


def validate_file(file: UploadFile) -> None:
    """Validate uploaded file."""
    # Check filename
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )
    
    # Check extension
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check content type (if provided)
    if file.content_type:
        # Basic content type validation
        allowed_content_types = {
            "audio/", "video/", "text/", "application/pdf",
            "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
        if not any(file.content_type.startswith(ct) for ct in allowed_content_types):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content type not allowed"
            )


async def save_uploaded_file(file: UploadFile, project_id: int) -> Tuple[str, int]:
    """
    Save uploaded file to storage (local or SharePoint).
    
    Returns:
        tuple: (file_path, file_size)
    """
    # Validate file
    validate_file(file)
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Check file size
    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )
    
    # Save based on storage type
    if settings.STORAGE_TYPE.lower() == "sharepoint":
        # Upload to SharePoint
        file_path = await upload_file_to_sharepoint(
            content,
            file.filename or "unknown",
            project_id
        )
        
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to SharePoint"
            )
        
        return file_path, file_size
    elif settings.STORAGE_TYPE.lower() == "s3":
        # Upload to S3
        file_path = await upload_file_to_s3(
            content,
            file.filename or "unknown",
            project_id
        )
        
        if not file_path:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload file to S3"
            )
        
        return file_path, file_size
    else:
        # Save to local filesystem
        upload_dir = Path(settings.UPLOAD_DIR) / str(project_id)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_ext = get_file_extension(file.filename or "unknown")
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = upload_dir / unique_filename
        
        # Write file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Return relative path from uploads directory
        relative_path = str(file_path.relative_to(Path(settings.UPLOAD_DIR)))
        return relative_path, file_size


def delete_file(file_path: str) -> None:
    """Delete a file from storage (local, SharePoint, or S3)."""
    if settings.STORAGE_TYPE.lower() == "sharepoint":
        # Delete from SharePoint
        delete_file_from_sharepoint(file_path)
    elif settings.STORAGE_TYPE.lower() == "s3":
        # Delete from S3
        delete_file_from_s3(file_path)
    else:
        # Delete from local filesystem
        full_path = Path(settings.UPLOAD_DIR) / file_path
        if full_path.exists():
            full_path.unlink()


def get_file_content(file_path: str) -> Optional[bytes]:
    """
    Get file content from storage (local, SharePoint, or S3).
    
    Args:
        file_path: File path (relative for local, SharePoint path for SharePoint, S3 key for S3)
        
    Returns:
        File content as bytes or None if file not found
    """
    if settings.STORAGE_TYPE.lower() == "sharepoint":
        # Download from SharePoint
        return download_file_from_sharepoint(file_path)
    elif settings.STORAGE_TYPE.lower() == "s3":
        # Download from S3
        return download_file_from_s3(file_path)
    else:
        # Read from local filesystem
        full_path = Path(settings.UPLOAD_DIR) / file_path
        if full_path.exists():
            with open(full_path, "rb") as f:
                return f.read()
        return None
