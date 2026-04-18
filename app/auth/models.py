"""
Defines the structure of requests and responses for user authentication operations.
"""
from pydantic import BaseModel, ConfigDict, Field, EmailStr, model_validator
from uuid import UUID
from typing_extensions import Self
from app.entities.users import UserRole

from datetime import datetime



class UserBase(BaseModel):
    role: UserRole = Field(default=UserRole.STUDENT, description="The user's system role")


class UserCreate(UserBase):
    username: str = Field(max_length=30)
    first_name: str = Field(max_length=30)
    middle_name: str = Field(max_length=30)
    last_name: str = Field(max_length=30)
    email: EmailStr = Field(max_length=120)
    phone: str | None = None
    password: str = Field(min_length=8, max_length=15)
    password2: str = Field(min_length=8, max_length=15)
    ignore_name_conflict: bool = Field(default=False)

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        if self.password != self.password2:
            raise ValueError("Passwords do not match")
        return self



class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    # this makes behaves just like serializers in django for objects from the orm being sent out.

    id: UUID
    created_at: datetime

class  UserLogin(BaseModel):
    email_or_username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str


