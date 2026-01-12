import jwt
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from fastapi import Depends
from app.core.config import DATABASE_URL


from typing import Dict
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import HTTPException, status
from sqlalchemy import select
from app.models.users import User
from app.db.base import UserRole


DATABASE_URL = DATABASE_URL


engine = create_async_engine(DATABASE_URL, echo=True)


class Base(DeclarativeBase):
    pass


async_session = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_session():
    async with async_session() as session:
        yield session


session = Depends(get_session)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def create_access_token(data: Dict):
    to_encode = data.copy()
    expire = (datetime.now(timezone.utc) +
              timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_playload(token: str = Depends(oauth2_scheme)) -> str | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Токен устарел")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Ошибка авторизации")


async def get_current_user_from_token(session: AsyncSession =
                                      Depends(get_session),
                                      token_playload: dict =
                                      Depends(get_user_playload),
                                      token: str =
                                      Depends(oauth2_scheme)):
    user_id = token_playload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Токен не содержит" +
                            " идентификатора пользователя")
    try:
        user_id = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректный user_id в токене"
        )
    stmt = select(User).where(User.id == user_id)    #   type: ignore
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Пользователь не найден")
    return user


def require_role(*roles: UserRole):
    async def _role_checker(
        current_user: User = Depends(get_current_user_from_token)
                            ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return _role_checker
