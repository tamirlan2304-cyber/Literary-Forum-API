import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import CommentORM
from app.schemas.comment import CommentCreate, CommentUpdate


async def get_comments_by_post(db: AsyncSession, post_id: uuid.UUID, page: int = 1, size: int = 50) -> list[CommentORM]:
    result = await db.execute(
        select(CommentORM).where(CommentORM.post_id == post_id)
        .options(selectinload(CommentORM.author))
        .order_by(CommentORM.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    return result.scalars().all()


async def create_comment(db: AsyncSession, post_id: uuid.UUID, author_id: uuid.UUID, comment_data: CommentCreate) -> CommentORM:
    comment = CommentORM(
        post_id=post_id,
        author_id=author_id,
        content=comment_data.content
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    result = await db.execute(
        select(CommentORM).where(CommentORM.id ==comment.id)
        .options(selectinload(CommentORM.author))
    )
    return result.scalars().first()


async def update_comment(db: AsyncSession, comment: CommentORM, update_data: CommentUpdate) -> CommentORM:
    comment.content = update_data.content
    await db.commit()
    await db.refresh(comment)
    return comment


async def delete_comment(db: AsyncSession, comment: CommentORM) -> None:
    await db.delete(comment)
    await db.commit()


async def like_comment(db:AsyncSession, comment: CommentORM) -> CommentORM:
    comment.likes_count += 1
    await db.commit()
    await db.refresh(comment)
    return comment