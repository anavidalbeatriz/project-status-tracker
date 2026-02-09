"""
Security utilities for authentication and password hashing.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import hashlib

from app.core.config import settings

# Bcrypt has a 72-byte limit, so we hash longer passwords with SHA-256 first
BCRYPT_MAX_LENGTH = 72


def _prepare_password(password: str) -> bytes:
    """
    Prepare password for bcrypt hashing.
    If password is longer than 72 bytes, hash it with SHA-256 first.
    Returns bytes ready for bcrypt.
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > BCRYPT_MAX_LENGTH:
        # Hash with SHA-256 first, then use the hex digest (64 chars = 64 bytes)
        sha256_hash = hashlib.sha256(password_bytes).hexdigest()
        return sha256_hash.encode('utf-8')
    return password_bytes


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    Handles both short passwords and long passwords (pre-hashed with SHA-256).
    """
    try:
        # Try direct verification first
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        
        if bcrypt.checkpw(password_bytes, hashed_bytes):
            return True
        
        # If password is longer than 72 bytes, try with SHA-256 hash
        if len(password_bytes) > BCRYPT_MAX_LENGTH:
            sha256_hash = hashlib.sha256(password_bytes).hexdigest()
            if bcrypt.checkpw(sha256_hash.encode('utf-8'), hashed_bytes):
                return True
        
        return False
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    For passwords longer than 72 bytes, hash with SHA-256 first, then bcrypt.
    """
    prepared_password = _prepare_password(password)
    # Generate salt and hash the password
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(prepared_password, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
