"""
Transcription management endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.db.database import get_db
from app.db.models.transcription import Transcription
from app.db.models.project import Project
from app.db.models.user import User
from app.schemas.transcription import TranscriptionResponse, TranscriptionDetailResponse
from app.api.v1.endpoints.auth import get_current_user
from app.utils.file_upload import save_uploaded_file, get_file_type, delete_file
from app.services.openai_service import transcribe_audio_video, read_text_file

router = APIRouter()


async def process_transcription_background(
    transcription_id: int,
    file_path: str,
    file_type: str
):
    """Background task to process transcription and extract status."""
    from app.db.database import SessionLocal
    from app.db.models.project import Project
    from app.db.models.project_status import ProjectStatus
    from app.services.ai_status_extractor import extract_status_from_transcription, validate_extracted_status
    import logging
    
    logger = logging.getLogger(__name__)
    db = SessionLocal()
    
    try:
        transcription = db.query(Transcription).filter(Transcription.id == transcription_id).first()
        if not transcription:
            logger.warning(f"Transcription {transcription_id} not found")
            return
        
        raw_text = None
        
        if file_type in ["audio", "video"]:
            # Transcribe audio/video using OpenAI Whisper
            logger.info(f"Starting transcription for {transcription_id}")
            raw_text = await transcribe_audio_video(file_path)
            logger.info(f"Transcription completed for {transcription_id}")
        elif file_type == "text":
            # Read text file directly
            raw_text = read_text_file(file_path)
        
        if raw_text:
            transcription.raw_text = raw_text
            transcription.processed_at = func.now()
            db.commit()
            db.refresh(transcription)
            logger.info(f"Transcription {transcription_id} processed successfully")
            
            # Extract status from transcription using AI
            project = db.query(Project).filter(Project.id == transcription.project_id).first()
            if project:
                logger.info(f"Extracting status from transcription {transcription_id} for project {project.id}")
                
                # Get client name
                client_name = project.client.name if project.client else "Unknown"
                
                # Extract status using AI
                extracted_status = extract_status_from_transcription(
                    transcription_text=raw_text,
                    project_name=project.name,
                    client_name=client_name
                )
                
                if extracted_status:
                    # Validate and normalize the extracted data
                    validated_status = validate_extracted_status(extracted_status)
                    
                    # Create new project status record
                    project_status = ProjectStatus(
                        project_id=project.id,
                        is_on_scope=validated_status.get("is_on_scope"),
                        is_on_time=validated_status.get("is_on_time"),
                        is_on_budget=validated_status.get("is_on_budget"),
                        next_delivery=validated_status.get("next_delivery"),
                        risks=validated_status.get("risks"),
                        updated_by=transcription.created_by
                    )
                    
                    db.add(project_status)
                    db.commit()
                    logger.info(f"Status extracted and saved for project {project.id} from transcription {transcription_id}")
                else:
                    logger.warning(f"Failed to extract status from transcription {transcription_id}")
            else:
                logger.warning(f"Project not found for transcription {transcription_id}")
        else:
            logger.warning(f"No text extracted from transcription {transcription_id}")
    except Exception as e:
        # Log error but don't fail the request
        logger.error(f"Error processing transcription {transcription_id}: {str(e)}", exc_info=True)
    finally:
        db.close()


@router.get("/", response_model=List[TranscriptionResponse])
async def get_transcriptions(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all transcriptions, optionally filtered by project."""
    query = db.query(Transcription)
    
    if project_id is not None:
        query = query.filter(Transcription.project_id == project_id)
    
    transcriptions = query.all()
    return transcriptions


@router.get("/{transcription_id}", response_model=TranscriptionDetailResponse)
async def get_transcription(
    transcription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific transcription by ID."""
    transcription = db.query(Transcription).filter(Transcription.id == transcription_id).first()
    if transcription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcription not found"
        )
    
    return transcription


@router.post("/", response_model=TranscriptionResponse, status_code=status.HTTP_201_CREATED)
async def upload_transcription(
    background_tasks: BackgroundTasks,
    project_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a transcription file for a project."""
    # Verify project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Save file
    try:
        file_path, file_size = await save_uploaded_file(file, project_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving file: {str(e)}"
        )
    
    # Determine file type
    file_type = get_file_type(file.filename)
    
    # Create transcription record
    db_transcription = Transcription(
        project_id=project_id,
        file_path=file_path,
        file_name=file.filename,
        file_type=file_type,
        file_size=file_size,
        created_by=current_user.id
    )
    
    db.add(db_transcription)
    db.commit()
    db.refresh(db_transcription)
    
    # Process transcription in background (for audio/video) or immediately (for text)
    if file_type == "text":
        # Read text file immediately
        raw_text = read_text_file(file_path)
        if raw_text:
            db_transcription.raw_text = raw_text
            db_transcription.processed_at = func.now()
            db.commit()
            db.refresh(db_transcription)
            
            # Extract status from text file immediately
            from app.db.models.project_status import ProjectStatus
            from app.services.ai_status_extractor import extract_status_from_transcription, validate_extracted_status
            
            client_name = project.client.name if project.client else "Unknown"
            extracted_status = extract_status_from_transcription(
                transcription_text=raw_text,
                project_name=project.name,
                client_name=client_name
            )
            
            if extracted_status:
                validated_status = validate_extracted_status(extracted_status)
                project_status = ProjectStatus(
                    project_id=project.id,
                    is_on_scope=validated_status.get("is_on_scope"),
                    is_on_time=validated_status.get("is_on_time"),
                    is_on_budget=validated_status.get("is_on_budget"),
                    next_delivery=validated_status.get("next_delivery"),
                    risks=validated_status.get("risks"),
                    updated_by=current_user.id
                )
                db.add(project_status)
                db.commit()
    else:
        # Process audio/video in background
        background_tasks.add_task(
            process_transcription_background,
            db_transcription.id,
            file_path,
            file_type
        )
    
    return db_transcription


@router.delete("/{transcription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transcription(
    transcription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a transcription and its associated file."""
    transcription = db.query(Transcription).filter(Transcription.id == transcription_id).first()
    if transcription is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transcription not found"
        )
    
    # Delete file if it exists
    if transcription.file_path:
        try:
            delete_file(transcription.file_path)
        except Exception as e:
            # Log error but continue with database deletion
            pass
    
    db.delete(transcription)
    db.commit()
    
    return None
