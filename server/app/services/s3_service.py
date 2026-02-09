"""
AWS S3 service for file storage.
"""
import logging
import uuid
from pathlib import Path
from typing import Optional
from io import BytesIO

try:
    import boto3
    from botocore.exceptions import ClientError, BotoCoreError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_s3_client():
    """Get S3 client instance."""
    if not S3_AVAILABLE:
        logger.error("boto3 is not installed. Install it with: pip install boto3")
        return None
    
    try:
        s3_client = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID if hasattr(settings, 'AWS_ACCESS_KEY_ID') else None,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY if hasattr(settings, 'AWS_SECRET_ACCESS_KEY') else None
        )
        return s3_client
    except Exception as e:
        logger.error(f"Failed to create S3 client: {str(e)}")
        return None


async def upload_file_to_s3(
    file_content: bytes,
    filename: str,
    project_id: int,
    folder_path: Optional[str] = None
) -> Optional[str]:
    """
    Upload file to S3.
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        project_id: Project ID for folder organization
        folder_path: Optional custom folder path
        
    Returns:
        S3 object key (path) or None if upload fails
    """
    if not S3_AVAILABLE:
        logger.error("boto3 is not available")
        return None
    
    s3_client = get_s3_client()
    if not s3_client:
        return None
    
    try:
        # Generate unique filename
        file_ext = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Determine S3 key (path)
        if folder_path:
            s3_key = f"{folder_path}/{unique_filename}"
        else:
            # Use project_id as folder name
            s3_key = f"projects/{project_id}/{unique_filename}"
        
        # Upload file
        s3_client.upload_fileobj(
            BytesIO(file_content),
            settings.AWS_S3_BUCKET,
            s3_key,
            ExtraArgs={'ContentType': 'application/octet-stream'}
        )
        
        logger.info(f"File uploaded to S3: s3://{settings.AWS_S3_BUCKET}/{s3_key}")
        return s3_key
        
    except ClientError as e:
        logger.error(f"AWS S3 error uploading file: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error uploading file to S3: {str(e)}")
        return None


def download_file_from_s3(s3_key: str) -> Optional[bytes]:
    """
    Download file from S3.
    
    Args:
        s3_key: S3 object key (path)
        
    Returns:
        File content as bytes or None if download fails
    """
    if not S3_AVAILABLE:
        logger.error("boto3 is not available")
        return None
    
    s3_client = get_s3_client()
    if not s3_client:
        return None
    
    try:
        response = s3_client.get_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=s3_key
        )
        return response['Body'].read()
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            logger.warning(f"File not found in S3: {s3_key}")
        else:
            logger.error(f"AWS S3 error downloading file: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error downloading file from S3: {str(e)}")
        return None


def delete_file_from_s3(s3_key: str) -> bool:
    """
    Delete file from S3.
    
    Args:
        s3_key: S3 object key (path)
        
    Returns:
        True if deletion successful, False otherwise
    """
    if not S3_AVAILABLE:
        logger.error("boto3 is not available")
        return False
    
    s3_client = get_s3_client()
    if not s3_client:
        return False
    
    try:
        s3_client.delete_object(
            Bucket=settings.AWS_S3_BUCKET,
            Key=s3_key
        )
        logger.info(f"File deleted from S3: s3://{settings.AWS_S3_BUCKET}/{s3_key}")
        return True
        
    except ClientError as e:
        logger.error(f"AWS S3 error deleting file: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error deleting file from S3: {str(e)}")
        return False


def get_file_url_from_s3(s3_key: str, expires_in: int = 3600) -> Optional[str]:
    """
    Get a presigned URL for an S3 object.
    
    Args:
        s3_key: S3 object key (path)
        expires_in: URL expiration time in seconds (default: 1 hour)
        
    Returns:
        Presigned URL or None if generation fails
    """
    if not S3_AVAILABLE:
        logger.error("boto3 is not available")
        return None
    
    s3_client = get_s3_client()
    if not s3_client:
        return None
    
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': settings.AWS_S3_BUCKET, 'Key': s3_key},
            ExpiresIn=expires_in
        )
        return url
    except Exception as e:
        logger.error(f"Error generating presigned URL: {str(e)}")
        return None
