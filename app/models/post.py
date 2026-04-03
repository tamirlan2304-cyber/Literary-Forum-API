import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Boolean, DateTime, String, Integer, func, Table, Column, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", UUID(as_uuid=True),ForeignKey("posts.id", ondelete="CASCADE"),  primary_key=True),
    Column("tag_id", Integer,ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

class PostORM(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text)
    likes_count: Mapped[int]  = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # ---- Связи (relationships) ----

    author: Mapped["UserORM"] = relationship(back_populates="posts")
    comments: Mapped[list["CommentORM"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    tags: Mapped[list["TagORM"]] = relationship(secondary=post_tags, back_populates="posts")