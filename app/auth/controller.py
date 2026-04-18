"""
Authentication routes.

This module exposes endpoints used for user registration, login, token refresh and logout.
It delegates actual authenticationwork to `app.auth.service` and uses rate limiting for
expensive endpoints.
"""
from typing import Any
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from app.auth import models
from app.auth import service
from app.database.core import db_dependency
from app.limiter.rate_limiter import limiter

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/create-user/",
    response_model=models.UserResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
async def create_user(
    request: Request, create_user_request: models.UserCreate, db: db_dependency
) -> Any:
    """
    Create a new user record.
    """
    return service.create_user(db, create_user_request)

@router.post("/access-token", response_model=models.Token, status_code=status.HTTP_200_OK)
async def login_for_tokens(
    login_payload: models.UserLogin, db: db_dependency
):
    """
    Authenticate credentials and return access and refresh tokens.
    """
    tokens: models.Token = service.login_for_tokens(login_payload, db)
    return tokens


@router.post("/refresh", response_model=models.Token, status_code=status.HTTP_200_OK) # this handle refresh_token as query_param
async def refresh_access_token(
        payload: models.RefreshTokenRequest,
        db: db_dependency
):
    """
    Exchange a refresh token for a new access token pair.
    """
    new_tokens: models.Token = service.get_refresh_access_tokens(payload.refresh_token, db)
    return new_tokens


@router.post("/logout") # this handle refresh_token as query_param
async def logout(
        payload: models.RefreshTokenRequest,
        db: db_dependency
):
    """
    Invalidate an existing refresh token to log the user out.
    """
    message = service.logout(payload.refresh_token, db)

    return JSONResponse(content=message, status_code=status.HTTP_200_OK)
