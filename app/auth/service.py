"""
Authentication service functions.

Contains the core business logic for user registration, credential and social
authentication, token generation and logout. These functions are called by
the auth controller and translate DB and validation errors into HTTP
exceptions appropriate for API responses.
"""
from datetime import timedelta,datetime, UTC
from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import MultipleResultsFound

import logging

from app.auth.utils.security import (
    verify_password,
    hash_password,
    hash_token,
    create_access_token,
    create_refresh_token
)
from app.entities.users import User
from app.entities.auth_tables import RefreshToken
from app.auth.models import UserCreate, Token, UserLogin
from app.config import settings


def create_user(db: Session, create_user_request: UserCreate) -> User:
    """
    Register a new user in the system.
    """
    if create_user_request.password != create_user_request.password2:
        logging.warning("password and confirm password do not match.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match."
        )

    try:
        # stating it as User.username instead of just user, ensures that we are only selecting username not the whole row
        result_username = db.execute(
            select(User.username).where(User.username == create_user_request.username)
        )
        existing_username = result_username.scalar_one_or_none()

        result_email = db.execute(
            select(User.email).where(User.email == create_user_request.email)
        )
        existing_email = result_email.scalar_one_or_none()

    except MultipleResultsFound as e:
        logging.error(f"Multiple results found in the database: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database integrity error: Multiple results found"
        ) from e

    if existing_username:
        logging.warning("attempt to create an account with already existing username ")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username already registered.",
        )

    if existing_email:
        logging.warning("attempt to create an account with already existing email.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered."
        )

    try:
        new_user = User(
            username=str(create_user_request.username),
            email=str(create_user_request.email),
            hashed_password=hash_password(create_user_request.password),
            phone=create_user_request.phone,
            role=create_user_request.role,
        )
        db.add(new_user)
        db.commit()
        return new_user

    except Exception as e:
        db.rollback()
        logging.error(
            f"Failed to register user: {create_user_request.email}, Error: {str(e)}"
        )
        raise


def authenticate_user(email_or_username: str, password: str, db: Session) -> User | bool:
    """
    Authenticate a user using email or username and a plaintext password.
    """
    # try to find by username first
    try:
        result = db.execute(select(User).where(User.username == email_or_username))
        user: User | None = result.scalar_one_or_none()
    except MultipleResultsFound as e:
        logging.warning("Multiple users found with same username")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Multiple users found with same username",
        ) from e

    if not user:
        try:
            result = db.execute(select(User).where(User.email == email_or_username))
            user = result.scalar_one_or_none()
        except MultipleResultsFound as e:
            logging.warning("multiple users found with same email.")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Multiple users found with same email",
            ) from e  # this ensures the original exception is preserved in the output

    if not user or not verify_password(password, str(user.hashed_password)):
        logging.warning(
            f"Failed authentication attempt for email_or_username: {email_or_username}"
        )
        return False

    return user


def generate_refresh_access_token_pair(user: User, db: Session) -> Token:
    """
    Create an access token and a refresh token for the provided user.
    """
    access_token: str = create_access_token(
        user=user,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token: str = create_refresh_token(
        user_id=user.id,
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        db=db
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )

def login_for_tokens(
    login_payload: UserLogin, db: Session
) -> Token:
    """
    Authenticate a user and return access/refresh tokens.
    """
    user: User = authenticate_user(
        login_payload.email_or_username, login_payload.password, db
    )
    if not user:
        logging.error("Incorrect email/username or password.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incorrect email/username or password.",
        )

    return generate_refresh_access_token_pair(user=user, db=db)


def get_refresh_access_tokens(refresh_token: str, db: Session) -> Token:
    """
    Validate a refresh token, revoke it (rotate) and return a new token pair.
    """
    token_hash = hash_token(refresh_token)

    result = db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False
        )
    )
    stored_token = result.scalar_one_or_none()

    if not stored_token:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if stored_token.expires_at < datetime.now(UTC):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user = stored_token.user

    # We rotate the just used refresh token and make invalid for any other use (setting revoked to True)
    stored_token.revoked = True

    # creating a new pair of refresh and access token
    return generate_refresh_access_token_pair(user=user, db=db)


def logout(refresh_token: str, db: Session) -> dict:
    """
    Invalidate a refresh token to log the user out.
    """
    token_hash = hash_token(refresh_token)

    result = db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False
        )
    )
    stored_token = result.scalar_one_or_none()

    if stored_token:
        stored_token.revoked = True
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    return {"message": "logout successfully"}