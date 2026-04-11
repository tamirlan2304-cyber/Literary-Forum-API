import uuid
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.crud.user import get_user_by_id
from app.db.session import AsyncSessionLocal
from app.models.user import UserORM


bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


async def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
        db: AsyncSession = Depends(get_db),
        redis: aioredis.Redis = Depends(get_redis)
) -> UserORM:

    credentials_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exeption

    token = credentials.credentials

    is_blacklisted = await redis.get(f"blacklist:{token}")
    if is_blacklisted:
        raise credentials_exeption

    try:
        payload = decode_access_token(token)
        user_id : str = payload.get("sub")
        if user_id is None:
            raise credentials_exeption
    except JWTError:
        raise credentials_exeption

    user = await get_user_by_id(db, uuid.UUID(user_id))
    if user is None or not user.is_active:
        raise credentials_exeption

    return user


CurrentUser = Depends(get_current_user)






