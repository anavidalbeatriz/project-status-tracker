"""
SharePoint service for file storage.
"""
import logging
import uuid
from pathlib import Path
from typing import Optional
from io import BytesIO

try:
    from office365.sharepoint.client_context import ClientContext
    from office365.runtime.auth.client_credential import ClientCredential
    from office365.sharepoint.files.file import File
    SHAREPOINT_AVAILABLE = True
except ImportError:
    SHAREPOINT_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_sharepoint_client() -> Optional[ClientContext]:
    """Get authenticated SharePoint client context."""
    if not SHAREPOINT_AVAILABLE:
        logger.error("Office365-REST-Python-Client not installed. Install with: pip install Office365-REST-Python-Client")
        return None
    
    if not all([
        settings.SHAREPOINT_SITE_URL,
        settings.SHAREPOINT_CLIENT_ID,
        settings.SHAREPOINT_CLIENT_SECRET,
        settings.SHAREPOINT_TENANT_ID
    ]):
        logger.error("SharePoint configuration incomplete. Please set all SharePoint environment variables.")
        return None
    
    try:
        credentials = ClientCredential(
            settings.SHAREPOINT_CLIENT_ID,
            settings.SHAREPOINT_CLIENT_SECRET
        )
        
        ctx = ClientContext(settings.SHAREPOINT_SITE_URL).with_credentials(credentials)
        # Test connection
        web = ctx.web
        ctx.load(web)
        ctx.execute_query()
        
        logger.info("Successfully authenticated with SharePoint")
        return ctx
    except Exception as e:
        logger.error(f"Failed to authenticate with SharePoint: {str(e)}")
        return None


async def upload_file_to_sharepoint(
    file_content: bytes,
    filename: str,
    project_id: int,
    folder_path: Optional[str] = None
) -> Optional[str]:
    """
    Upload file to SharePoint.
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        project_id: Project ID for folder organization
        folder_path: Optional custom folder path
        
    Returns:
        SharePoint file path/URL or None if upload fails
    """
    ctx = get_sharepoint_client()
    if not ctx:
        return None
    
    try:
        # Generate unique filename
        file_ext = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Determine folder path
        if folder_path:
            target_folder = folder_path
        else:
            # Use project_id as folder name
            target_folder = f"{settings.SHAREPOINT_DOCUMENT_LIBRARY}/{project_id}"
        
        # Get the target folder
        target_folder_obj = ctx.web.get_folder_by_server_relative_url(target_folder)
        
        # Create folder if it doesn't exist
        try:
            ctx.load(target_folder_obj)
            ctx.execute_query()
        except:
            # Folder doesn't exist, create it
            parent_folder = ctx.web.get_folder_by_server_relative_url(settings.SHAREPOINT_DOCUMENT_LIBRARY)
            target_folder_obj = parent_folder.folders.add(f"{project_id}")
            ctx.execute_query()
        
        # Upload file using BytesIO for file-like object
        file_stream = BytesIO(file_content)
        
        uploaded_file = target_folder_obj.upload_file(unique_filename, file_stream).execute_query()
        
        # Return relative path (server-relative URL format)
        file_path = f"{target_folder}/{unique_filename}"
        logger.info(f"File uploaded to SharePoint: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error uploading file to SharePoint: {str(e)}")
        return None


def download_file_from_sharepoint(file_path: str) -> Optional[bytes]:
    """
    Download file from SharePoint.
    
    Args:
        file_path: SharePoint relative file path
        
    Returns:
        File content as bytes or None if download fails
    """
    ctx = get_sharepoint_client()
    if not ctx:
        return None
    
    try:
        file = ctx.web.get_file_by_server_relative_url(file_path)
        file_content = file.open_binary()
        ctx.execute_query()
        
        return file_content.content
        
    except Exception as e:
        logger.error(f"Error downloading file from SharePoint: {str(e)}")
        return None


def delete_file_from_sharepoint(file_path: str) -> bool:
    """
    Delete file from SharePoint.
    
    Args:
        file_path: SharePoint relative file path
        
    Returns:
        True if deletion successful, False otherwise
    """
    ctx = get_sharepoint_client()
    if not ctx:
        return False
    
    try:
        file = ctx.web.get_file_by_server_relative_url(file_path)
        file.delete_object()
        ctx.execute_query()
        
        logger.info(f"File deleted from SharePoint: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting file from SharePoint: {str(e)}")
        return False


def get_file_url_from_sharepoint(file_path: str) -> Optional[str]:
    """
    Get download URL for a file in SharePoint.
    
    Args:
        file_path: SharePoint relative file path
        
    Returns:
        File download URL or None
    """
    ctx = get_sharepoint_client()
    if not ctx:
        return None
    
    try:
        file = ctx.web.get_file_by_server_relative_url(file_path)
        ctx.load(file, ["ServerRelativeUrl"])
        ctx.execute_query()
        
        # Construct full URL
        base_url = settings.SHAREPOINT_SITE_URL.rstrip('/')
        return f"{base_url}{file.properties['ServerRelativeUrl']}"
        
    except Exception as e:
        logger.error(f"Error getting file URL from SharePoint: {str(e)}")
        return None
