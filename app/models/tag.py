import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.post import post_tags

class TagORM(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[String] = mapped_column(String(50), unique=True, nullable=False, index=True)

    posts: Mapped[list["PostORM"]] = relationship(back_populates="tags", secondary=post_tags)