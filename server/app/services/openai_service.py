"""
OpenAI service for transcription and AI processing.
"""
import os
import logging
from pathlib import Path
from typing import Optional
from openai import OpenAI

from app.core.config import settings
from app.utils.file_upload import get_file_content

logger = logging.getLogger(__name__)

# Initialize OpenAI client (lazy initialization to avoid errors if API key is not set)
_client = None
_client_initialized = False

def get_openai_client():
    """Get OpenAI client, initializing it if needed."""
    global _client, _client_initialized
    
    if not _client_initialized:
        _client_initialized = True
        if settings.OPENAI_API_KEY:
            try:
                _client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                _client = None
        else:
            logger.warning("OpenAI API key not configured. Transcription features will be disabled.")
            _client = None
    
    return _client


async def transcribe_audio_video(file_path: str) -> Optional[str]:
    """
    Transcribe audio or video file using OpenAI Whisper API.
    
    Args:
        file_path: Path to the audio/video file
        
    Returns:
        Transcribed text or None if transcription fails
    """
    openai_client = get_openai_client()
    if not openai_client:
        logger.error("OpenAI client not initialized. Please configure OPENAI_API_KEY.")
        return None
    
    try:
        # Get file content (works for both local and SharePoint)
        file_content = get_file_content(file_path)
        
        if not file_content:
            logger.error(f"File not found or could not be read: {file_path}")
            return None
        
        # Get filename from path for content type detection
        full_path = Path(file_path)
        
        # Transcribe file
        logger.info(f"Transcribing file: {file_path}")
        
        # Determine content type based on file extension
        ext = full_path.suffix.lower()
        content_type_map = {
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".m4a": "audio/mp4",
            ".ogg": "audio/ogg",
            ".flac": "audio/flac",
            ".webm": "audio/webm",
            ".mp4": "video/mp4",
            ".avi": "video/x-msvideo",
            ".mov": "video/quicktime",
            ".mkv": "video/x-matroska",
        }
        content_type = content_type_map.get(ext, "audio/mpeg")
        
        # Create file tuple for OpenAI API: (filename, file_content, content_type)
        transcription = openai_client.audio.transcriptions.create(
            model="whisper-1",
            file=(full_path.name, file_content, content_type),
            response_format="text"
        )
        
        # When response_format="text", the API returns a string directly
        if isinstance(transcription, str):
            logger.info(f"Transcription completed. Length: {len(transcription)} characters")
            return transcription
        
        # Fallback: if response is an object with text attribute
        if hasattr(transcription, 'text'):
            text = transcription.text
            logger.info(f"Transcription completed. Length: {len(text)} characters")
            return text
        
        logger.warning(f"Unexpected transcription response format: {type(transcription)}")
        return None
            
    except Exception as e:
        logger.error(f"Error transcribing file {file_path}: {str(e)}")
        return None


def read_text_file(file_path: str) -> Optional[str]:
    """
    Read text from a text file (local or SharePoint).
    
    Args:
        file_path: Path to the text file
        
    Returns:
        File contents as string or None if reading fails
    """
    try:
        # Get file content (works for both local and SharePoint)
        file_content = get_file_content(file_path)
        
        if not file_content:
            logger.error(f"File not found or could not be read: {file_path}")
            return None
        
        # Try decoding as UTF-8
        try:
            return file_content.decode("utf-8")
        except UnicodeDecodeError:
            # If UTF-8 fails, try with error handling
            return file_content.decode("utf-8", errors="ignore")
                
    except Exception as e:
        logger.error(f"Error reading text file {file_path}: {str(e)}")
        return None
