"""
Security utility helpers for authentication.

Provides password hashing/verification, JWT access token creation and
refresh token generation and verification helpers used across the auth
service.
"""

import logging

from sqlalchemy.orm import Session
from app.entities.users import User
#for access token creation
import bcrypt
from jose import JWTError, jwt

# for refresh token creation
import secrets
import hashlib

from uuid import UUID
from datetime import timedelta, datetime, UTC

from app.config import settings
from app.entities.auth_tables import RefreshToken
from typing import cast
from fastapi import HTTPException, status


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hashed password.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt and return the encoded string.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def verify_token(token: str, db: Session) -> User:
    """
    Decode a JWT access token and return the associated User.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("id")

        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")

        user = cast(User | None, db.get(User, UUID(user_id)))
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="user no longer exists"
            )

        return user

    except JWTError as e:
        logging.warning(f"Token verification failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="bad token or expired token"
        ) from e


def hash_token(token:str) -> str:
    """
    Create an SHA-256 hex digest from the provided token string.
    """

    hash_object = hashlib.sha256()
    hash_object.update(token.encode("utf-8")) # type checker issue, works perfectly fine.
    return hash_object.hexdigest()


def create_access_token(user: User, expires_delta: timedelta) -> str:
    """
    Create a signed JWT access token for the provided user.
    """
    encode = {
        "sub": user.email,
        "id": str(user.id), # always type cast this because the jwt lib does not accept UUID objects.
        "iat": int(datetime.now(UTC).timestamp()),
    }
    expires_at = datetime.now(UTC) + expires_delta
    encode.update({"exp": int(expires_at.timestamp())})

    return jwt.encode(encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: UUID, expires_delta: timedelta, db: Session) -> str:
    """
    Generate a secure refresh token string, persist a hashed representation
    in the DB and return the plaintext token to the caller.
    """
    refresh_token_str = secrets.token_urlsafe(64)
    refresh_token_hash = hash_token(refresh_token_str)

    expires_at = datetime.now(UTC) + expires_delta

    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=refresh_token_hash,
        expires_at=expires_at
    )
    db.add(refresh_token)
    db.commit()
    db.refresh(refresh_token)

    return refresh_token_str

