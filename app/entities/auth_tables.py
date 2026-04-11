"""
this module is for db entities that play roles in authentication of the user
"""

from typing import TYPE_CHECKING
from app.database.core import Base
from sqlalchemy import Uuid, ForeignKey, String, DateTime, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import UUID, uuid4

if TYPE_CHECKING:
    from app.entities.users import User


class RefreshToken(Base):
    """entity to offer refresh tokens."""

    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    token_hash: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    # user_agent: Mapped[str | None]
    # ip_address: Mapped[str| None]

    """relationships"""
    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")
