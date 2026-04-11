"""
Authentication dependencies for endpoints.

Provides an OAuth2 password bearer instance and helper dependencies to obtain
and validate the current user and enforce role-based access in route handlers.
"""

from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends, HTTPException, status
from app.entities.users import User, UserRole
from app.auth.utils.security import verify_token
from app.database.core import db_dependency

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/access-token") # tokenUrl is passed in for Swagger documentation.


async def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)],
    db: db_dependency
) -> User:
    """
    Resolve and return the current authenticated user using the provided
    bearer token.
    """
    return verify_token(token, db=db)


def require_role(*allowed_roles: UserRole):

    """
    Factory that returns a dependency enforcing that the current user has one
    of the specified roles.
    """

    def role_checker(user: Annotated[User, Depends(get_current_user)]) -> User:
        allowed_roles_set = set(allowed_roles)
        if user.role not in allowed_roles_set:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return user

    return role_checker
