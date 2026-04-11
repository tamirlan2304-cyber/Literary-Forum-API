import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.core.security import get_password_hash, verify_password # надо дописать
from app.models.user import UserORM
from app.schemas.user import UserCreate, UserUpdate

async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> UserORM | None:
    result = await db.execute(
        select(UserORM).where(UserORM.id == user_id)
    )
    return result.scalars().first()

async def get_user_by_email(db: AsyncSession, email: str) -> UserORM | None:
    result = await db.execute(
        select(UserORM).where(UserORM.email == email)
    )
    return result.scalars().first()

async def get_user_by_username(db: AsyncSession, username: str) -> UserORM | None:
    result = await db.execute(
        select(UserORM).where(UserORM.username == username)
    )
    return result.scalars().first()

async def create_user(db: AsyncSession, user_data: UserCreate) -> UserORM:
    user = UserORM(
        username = user_data.username,
        email = user_data.email,
        hashed_password = get_password_hash(user_data.password)
    )

    db.add(user)
    await db.commit()
    await db.refresh(user) # повторить refresh

    return user

async def authenticate_user(db: AsyncSession, email: str, password : str) -> UserORM | None:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


