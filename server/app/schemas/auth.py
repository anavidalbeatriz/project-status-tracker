"""
Authentication schemas.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token data schema."""
    email: Optional[str] = None


class UserLogin(BaseModel):
    """User login request schema."""
    email: EmailStr
    password: str


class UserRegister(BaseModel):
    """User registration request schema."""
    email: EmailStr
    password: str
    name: str
