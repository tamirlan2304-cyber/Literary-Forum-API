from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

import app.crud.user as crud
from app.core.dependencies import get_db
from app.core.security import create_access_token
from app.models import UserORM
from app.schemas.auth import TokenResponse
from app.schemas.user import UserCreate, UserResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code = 201)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):

    if await crud.get_user_by_email(db, user_data.email):
        raise HTTPException(status_code=400, detail="Email уже занят")
    if await crud.get_user_by_username(db, user_data.username):
        raise HTTPException(status_code=400, detail="Username уже занят")

    user = await crud.create_user(db, user_data)
    return user

@router.post("/login", response_model=TokenResponse)
async def login(email: str, password: str, db: AsyncSession = Depends(get_db)):
    user = await crud.authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )
    token = create_access_token(subject=str(user.id))
    return TokenResponse(access_token=token)




