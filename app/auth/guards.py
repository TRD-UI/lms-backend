"""
Convenience role guard dependencies.

Exports small dependency functions that enforce specific user roles. They are
thin wrappers around `require_role` for clearer usage in route definitions.
"""

from fastapi import Depends
from app.entities.users import User, UserRole
from app.auth.dependencies import require_role
from typing import Annotated


def require_teacher(
        user: Annotated[User, Depends(require_role(UserRole.INSTRUCTOR))]
) -> User:
    """Dependency that ensures the current user has the TEACHER role."""
    return user


def require_student(
        user: Annotated[User, Depends(require_role(UserRole.STUDENT))]
) -> User:
    """Dependency that ensures the current user has the STUDENT role."""
    return user


def require_admin(
        user: Annotated[User, Depends(require_role(UserRole.ADMIN))]
) -> User:
    """Dependency that ensures the current user has the ADMIN role."""
    return user