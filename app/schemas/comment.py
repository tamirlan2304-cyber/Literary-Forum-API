import uuid
from pydantic import BaseModel, EmailStr, field_validator, ValidationError
from datetime import datetime

from app.schemas.tag import TagResponse
from app.schemas.user import UserShort

class CommentCreate(BaseModel):
    content: str

    @field_validator('content')
    @classmethod
    def validate_content(cls, value : str) -> str:
        if len(value) < 10:
            raise ValidationError('Content must be at least 10 characters')
        return value

class CommentUpdate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: uuid.UUID
    content: str
    likes_count: int
    created_at: datetime
    updated_at: datetime
    author: UserShort

    model_config = {"from_attributes": True}
