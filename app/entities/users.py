"""
User and social account ORM entities.

Defines the SQLModel/SQLAlchemy ORM mappings for `User`.
These classes represent application users and their roles.
"""
from __future__ import (
    annotations,
)  # this is for use by older python version that do not support forward reference.
import enum
from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, Uuid, func, Boolean, Enum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional
from app.database.core import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    """
    this works to help avoid circular imports by turning of static type checking
    at runtime but leaving it on while coding so the pycharm would not complain.
    """
    from app.entities.profiles import InstructorProfile, StudentProfile
    from app.entities.auth_tables import RefreshToken


class UserRole(enum.Enum):
    """Enumerates supported application user roles."""
    ADMIN = "admin"
    INSTRUCTOR  = "instructor"
    STUDENT = "student"


class User(Base):
    """ORM mapping for application users.

    Attributes mirror database columns for email, password, verification
    flags and role. Relationships to profile and token tables are defined
    to allow eager access in services and controllers.
    """
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    username: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False  # we might use a library to generate a random username by default
    )
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    phone: Mapped[str | None] = mapped_column(String(24), nullable=True)
    is_email_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    is_phone_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    hashed_password: Mapped[str] = mapped_column(String, nullable=True)  # nullable due to social auth
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=True), nullable=False, default=UserRole.STUDENT
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    """relationships"""
    instructor_profile: Mapped[Optional["InstructorProfile"]] = relationship(
        "InstructorProfile", back_populates="user", uselist=False
    )
    student_profile: Mapped[Optional["StudentProfile"]] = relationship(
        "StudentProfile", back_populates="user", uselist=False
    )
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        """Return an informative representation used in logs and debugging."""
        return f"User(id= '{self.id}', email='{self.email}', phone='{self.phone}', role='{self.role}', created_at='{self.created_at}' )"
