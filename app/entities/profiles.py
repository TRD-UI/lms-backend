"""
this module is the module contains classes for the database entity for profiles
that actually map to database tables. It also contains the expertise table that
contains pool of expertise of the instructors.
"""
from datetime import datetime, date
from operator import index
from uuid import UUID, uuid4
import enum
from sqlalchemy import String, Uuid, ForeignKey, DateTime, func, Table, Column, Date, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.core import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    """
    this works to help avoid circular imports by turning of static type checking
    at runtime but leaving it on while coding so the pycharm would not complain.
    """
    # from app.entities.courses import Enrollment
    from app.entities.users import User

class Gender(enum.Enum):
    """this is to enumerate the available genders available"""
    MALE = "male"
    FEMALE = "female"

# using a standard join table that does not map to a python class
# as there is no need for extra columns on the join table.
instructor_expertise = Table(
    "instructor_expertise",
    Base.metadata,
    Column("expertise_id", ForeignKey("expertise.id"), primary_key=True),
    Column("instructor_profile_id", ForeignKey("instructor_profile.id"), primary_key=True),
)


class Expertise(Base):
    """Entity for pool of different expertise. admin can add new expertise to the pool."""

    __tablename__ = "expertise"
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    instructor_profiles: Mapped[list["InstructorProfile"]] = relationship(
        "InstructorProfile", secondary=instructor_expertise, back_populates="expertise"
    )


class InstructorProfile(Base):
    """Entity for all instructors profiles"""

    __tablename__ = "instructor_profile"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    bio: Mapped[str | None] = mapped_column(String(300), nullable=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    address:  Mapped[str | None] = mapped_column(String(60), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender] = mapped_column(
        Enum(Gender, native_enum=True), nullable=False, default=Gender.MALE
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    """relationships."""

    user: Mapped["User"] = relationship("User", back_populates="instructor_profile")
    expertise: Mapped[list["Expertise"]] = relationship(
        "Expertise", secondary=instructor_expertise, back_populates="instructor_profiles"
    )
    # courses: Mapped[list["Course"]] = relationship("Course", back_populates="instructor_profile")


class StudentProfile(Base):
    """Entity for all students profiles"""

    __tablename__ = "student_profile"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[Gender] = mapped_column(
        Enum(Gender, native_enum=True), nullable=False, default=Gender.MALE
    )
    address: Mapped[str | None] = mapped_column(String(60), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    """relationships"""
    user: Mapped["User"] = relationship("User", back_populates="student_profile")

    # courses: Mapped[list["Course"]] = relationship(
    #     "Course",
    #     secondary="enrollments",
    #     viewonly=True,
    # )
    # enrollments: Mapped[list["Enrollment"]] = relationship(
    #     "Enrollment",
    #     back_populates="student_profile",
    #     cascade="all, delete-orphan",  # automatically deletes the enrollment when it is removed from the list of enrollment
    # )
    # course_ratings: Mapped[list["CourseRating"]] = relationship(
    #     "CourseRating", back_populates="student_profile", cascade="all, delete-orphan"
    # )
    __table_args__ = (
        Index("ix_user_full_name", "first_name", "last_name", "middle_name"),
    )
