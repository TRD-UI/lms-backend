"""
profiles are actually created on user sign-up by the backend automatically,
hence the only available profile endpoints would be for patch, get.
"""
from fastapi import APIRouter, status, Depends
from typing import Annotated

from app.auth.guards import require_student, require_instructor
from app.entities.users import User
from app.database.core import db_dependency
from app.profiles.models import StudentProfileResponse, InstructorProfileResponse, StudentProfileOut, InstructorProfileOut, StudentProfileUpdate, InstructorProfileUpdate
from app.profiles import service

router = APIRouter(
    prefix="/profiles",
    tags = ["profiles"],
)

@router.patch(
    "/student/me",
    response_model=StudentProfileResponse,
    status_code=status.HTTP_200_OK
)
async def update_student_profile(
        profile_data: StudentProfileUpdate,
        db: db_dependency,
        current_user: Annotated[User, Depends(require_student)]
):
    """update profile for the logged-in user."""
    return service.update_student_profile(db=db, user=current_user, payload=profile_data)

@router.get(
    "/student/me",
    response_model=StudentProfileOut,
    status_code=status.HTTP_200_OK
)
async def get_student_profile(
        db: db_dependency,
        current_user: Annotated[User, Depends(require_student)]
):
    return service.get_student_profile(db=db, user=current_user)

@router.patch(
    "/instructor/me",
    response_model=InstructorProfileResponse,
    status_code=status.HTTP_200_OK
)
async def update_instructor_profile(
        profile_data: InstructorProfileUpdate,
        db:db_dependency,
        current_user: Annotated[User, Depends(require_instructor)]
):
    """update profile for logged-in instructor"""
    return service.update_instructor_profile(db=db, user=current_user, payload=profile_data)

@router.get(
    "/instructor/me",
    response_model=InstructorProfileOut,
    status_code=status.HTTP_200_OK
)
async def get_instructor_profile(
        db:db_dependency,
        current_user: Annotated[User, Depends(require_instructor)]
):
    return service.get_instructor_profile(db=db, user=current_user)