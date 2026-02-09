"""
Application configuration settings.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3002,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # OpenAI
    OPENAI_API_KEY: str = ""
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 104857600  # 100MB
    UPLOAD_DIR: str = "uploads"
    STORAGE_TYPE: str = "local"  # "local", "sharepoint", or "s3"
    
    # SharePoint Configuration (if STORAGE_TYPE is "sharepoint")
    SHAREPOINT_SITE_URL: str = ""  # e.g., "https://yourtenant.sharepoint.com/sites/yoursite"
    SHAREPOINT_DOCUMENT_LIBRARY: str = "Documents"  # Document library name
    SHAREPOINT_CLIENT_ID: str = ""  # Azure AD App Registration Client ID
    SHAREPOINT_CLIENT_SECRET: str = ""  # Azure AD App Registration Client Secret
    SHAREPOINT_TENANT_ID: str = ""  # Azure AD Tenant ID
    
    # AWS S3 Configuration (if STORAGE_TYPE is "s3")
    AWS_S3_BUCKET: str = ""  # S3 bucket name
    AWS_REGION: str = "us-east-1"  # AWS region
    AWS_ACCESS_KEY_ID: str = ""  # AWS access key (or use IAM role)
    AWS_SECRET_ACCESS_KEY: str = ""  # AWS secret key (or use IAM role)
    
    # Environment
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
