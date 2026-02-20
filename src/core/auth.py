"""
Authentication utilities for the Fill application.

This module provides password hashing and JWT token creation/validation
functions. A minimal authentication framework for future expansion.
"""

from datetime import datetime, timedelta
from typing import Dict

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.config.settings import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token

    Returns:
        The encoded JWT token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> Dict | None:
    """
    Decode and verify a JWT access token.

    Args:
        token: The JWT token to decode

    Returns:
        The decoded token data, or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None

