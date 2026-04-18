from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime
from uuid import UUID
from app.entities.profiles import Gender
from typing import Optional


class BaseProfileInModel(BaseModel):
    first_name: str = Field(max_length=50)
    middle_name: Optional[str] = Field(max_length=50, default=None)
    last_name: str = Field(max_length=50)
    birth_date: Optional[date] = None
    gender: Optional[Gender] = Field(default=Gender.MALE)
    address: Optional[str] = Field(max_length=150, default=None)

class StudentProfileCreate(BaseProfileInModel):
    pass

class InstructorProfileCreate(BaseProfileInModel):
    bio: Optional[str] = Field(max_length=300, default=None)

class StudentProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime

class InstructorProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime

class BaseProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    birth_date: Optional[date] = None
    gender: Gender
    address: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class StudentProfileOut(BaseProfileOut):
    pass

class InstructorProfileOut(BaseProfileOut):
    bio: Optional[str] = None

class BaseProfileUpdate(BaseModel):
    first_name: Optional[str] = Field(max_length=50, default=None)
    middle_name: Optional[str] = Field(max_length=50, default=None)
    last_name: Optional[str] = Field(max_length=50, default=None)
    birth_date: Optional[date] = None
    gender: Optional[Gender] = None
    address: Optional[str] = Field(default=None, max_length=150)

class StudentProfileUpdate(BaseProfileUpdate):
    pass

class InstructorProfileUpdate(BaseProfileUpdate):
    bio: Optional[str] = Field(max_length=300, default=None)