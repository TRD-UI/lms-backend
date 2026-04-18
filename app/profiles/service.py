import logging
from app.entities.profiles import StudentProfile, InstructorProfile
from app.entities.users import User
from app.profiles.models import StudentProfileCreate, InstructorProfileCreate, StudentProfileUpdate, InstructorProfileUpdate

from sqlalchemy.orm import Session
from sqlalchemy import func, select, and_

from fastapi import HTTPException, status
from typing import cast

def get_existing_student_profile_by_names(db: Session, first: str, last: str, middle:str = None) -> StudentProfile | None:
    """Check if a student profile with matching names already exists."""
    query = select(StudentProfile).where(
        and_(
            func.lower(StudentProfile.first_name) == first.lower() ,
            func.lower(StudentProfile.last_name) == last.lower(),
            func.lower(StudentProfile.middle_name) == middle.lower() if middle else StudentProfile.middle_name.is_(None)
        )
    )
    return db.execute(query).scalars().first()

def create_student_profile(db: Session, user: User, profile_in: StudentProfileCreate) -> StudentProfile:
    """
    takes in a user instance and the payload for the profile, creates the profile and links it to the user instance.
    note that transaction control is now owned by the caller function"""
    existing = db.execute(select(StudentProfile).where(StudentProfile.user_id == user.id)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student profile already exists for this user."
        )
    new_profile = StudentProfile(
            user=user,
            first_name=profile_in.first_name,
            middle_name=profile_in.middle_name,
            last_name=profile_in.last_name,
            birth_date=profile_in.birth_date,
            gender=profile_in.gender,
            address=profile_in.address
        )
    db.add(new_profile)
    db.flush()
    return new_profile
    # any db transaction errors would be handled by create_user in auth/services.py since it calls this function

def get_student_profile(db: Session, user: User) -> StudentProfile:
    profile = db.execute(select(StudentProfile).where(StudentProfile.user_id == user.id)).scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")
    return profile

def update_student_profile(db: Session, user: User, payload: StudentProfileUpdate) -> StudentProfile:
    profile = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
    if not profile:
        logging.error("Attempt to update non-existing Student profile")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found"
        )

    update_dict = payload.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return cast(StudentProfile, profile)

def create_instructor_profile(db: Session, user: User, profile_in: InstructorProfileCreate) -> InstructorProfile:
    """
    takes in a user instance and the payload for the profile, creates the profile and links it to the user instance.
        note that transaction control is now owned by the caller function"""
    existing = db.execute(select(InstructorProfile).where(InstructorProfile.user_id == user.id)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Instructor profile already exists for this user."
        )
    new_profile = InstructorProfile(
            user=user,
            first_name=profile_in.first_name,
            middle_name=profile_in.middle_name,
            last_name=profile_in.last_name,
            bio=profile_in.bio,
            birth_date=profile_in.birth_date,
            gender=profile_in.gender,
            address=profile_in.address
        )
    db.add(new_profile)
    db.flush()
    return new_profile
    # any db transaction errors would be handled by create_user in auth/services.py since it calls this function


def get_instructor_profile(db: Session, user: User) -> InstructorProfile:
    profile = db.execute(select(InstructorProfile).where(InstructorProfile.user_id == user.id)).scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher profile not found.")
    return profile

def update_instructor_profile(db:Session, user: User, payload: InstructorProfileUpdate) -> InstructorProfile:
    profile = db.query(InstructorProfile).filter(InstructorProfile.user_id == user.id).first()
    if not profile:
        logging.error("Attempt to update non-existing Instructor profile")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Instructor profile not found"
        )

    update_dict = payload.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return cast(InstructorProfile, profile)
