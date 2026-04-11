import uuid

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.post import PostORM
from app.models.tag import TagORM
from app.schemas.post import PostCreate, PostUpdate

async def get_post_by_id(db: AsyncSession, post_id: uuid.UUID) -> PostORM:
    result = await db.execute(
        select(PostORM)
        .where(PostORM.id == post_id)
        .options(
            selectinload(PostORM.author),
            selectinload(PostORM.tags),
            selectinload(PostORM.comments)
        )
    )
    return result.scalars().first()


async def get_posts(db: AsyncSession, page: int = 1, size: int = 20, tag: str | None = None) -> tuple[list[PostORM], int]:
    query = select(PostORM).where(PostORM.is_published == True)

    if tag:
        query = query.join(PostORM.tags).where(TagORM.name == tag.lower())

    count_result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = count_result.scalar()

    result = await db.execute(
        query
        .options(
            selectinload(PostORM.author), selectinload(PostORM.tags))
        .order_by(PostORM.created_at.desc())
        .offset((page-1) * size)
        .limit(size)
    )
    posts = result.scalars().all()
    return posts, total


async def _get_or_create_tags(db: AsyncSession, tag_names: list[str]) -> list[TagORM]:
    tags = []
    for name in tag_names:
        name = name.strip().lower()

        result = await db.execute(select(TagORM).where(TagORM.name == name))
        tag = result.scalars().first()

        if not tag:
            tag = TagORM(name=name)
            db.add(tag)
            await db.flush()

        tags.append(tag)
    return tags


async def create_post(db: AsyncSession, post_data: PostCreate, author_id: uuid.UUID) -> PostORM:
    tags = await _get_or_create_tags(db, post_data.tag_names)

    post = PostORM(
        title = post_data.title,
        content = post_data.content,
        is_published = post_data.is_published,
        author_id = author_id,
        tags = tags
    )

    db.add(post)
    await db.commit()
    await db.refresh(post)

    return await get_post_by_id(db, post.id)


async def update_post(db: AsyncSession, post: PostORM, update_data: PostUpdate) -> PostORM:
    update_dict = update_data.model_dump(exclude_unset=True)

    if "tag_names" in update_dict:
        post.tags = await _get_or_create_tags(db, update_dict.pop("tag_names"))

    for field, value in update_dict.items():
        setattr(post, field, value)

    await db.commit()
    return await get_post_by_id(db, post.id)


async def delete_post(db: AsyncSession, post: PostORM) -> None:
    await db.delete(post)
    await db.commit()


async def like_post(db: AsyncSession, post: PostORM) -> PostORM:
    post.likes_count += 1
    await db.commit()
    await db.refresh(post)
    return post

