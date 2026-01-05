from app.schemas.users import UserCreate, UserLogin

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.users import User


async def create_user(user: User,
                      db: AsyncSession):
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_login(login: str,
                            db: AsyncSession):
    stmt = select(User).where((User.email == login) |
                              (User.username == login))    #   type: ignore
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_id(
    db: AsyncSession,
    user_id: int
) -> User | None:
    return await db.get(User, user_id)


async def set_user_password(
    db: AsyncSession,
    user: User,
    new_password_hash: str
) -> User:
    user.password_hash = new_password_hash
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(user: User,
                      db: AsyncSession):
    await db.delete(user)
    await db.commit()
