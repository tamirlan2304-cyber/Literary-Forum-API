import uuid
from pydantic import BaseModel, EmailStr, field_validator, ValidationError
from datetime import datetime

from app.schemas.tag import TagResponse
from app.schemas.user import UserShort


class PostBase(BaseModel):
    title: str
    content: str
    is_published: bool = True


class PostCreate(PostBase):
    tag_names: list[str] = []

    @field_validator("title")
    @classmethod
    def validate(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("title cannot be empty")
        return v

    @field_validator("title")
    @classmethod
    def min_lenght(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("title cannot be less than 10 characters")
        return v


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    is_published: bool | None = None
    tag_name: list[str] | None = None


class PostResponse(PostBase):
    id: uuid.UUID
    likes_count: int
    updated_at: datetime
    created_at: datetime

    author : UserShort
    tag : list[TagResponse] = []

    model_config = {"from_attributes": True}


class PostShort(BaseModel):
    id: uuid.UUID
    title: str
    likes_count: int
    created_at: datetime
    author: UserShort
    tags: list[TagResponse] = []

    model_config = {"from_attributes": True}


class PostListResponse(BaseModel):
    posts: list[PostShort]
    total: int
    page: int
    size: int