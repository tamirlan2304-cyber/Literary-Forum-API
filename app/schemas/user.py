import uuid
from pydantic import BaseModel, EmailStr, field_validator, ValidationError
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    @classmethod
    def password_len(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserUpdate(UserBase):
    username: str | None = None
    email: EmailStr | None = None

class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class UserShort(BaseModel):
    id: uuid.UUID
    username: str

    model_config = {"from_attributes": True}

