from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.prices import price_create as price_create_serv
from app.schemas.prices import PriceCreate
from app.models.prices import Price
from app.models.users import User

from app.dependencies import get_session, get_current_user_from_token


async def price_create(
        sub: PriceCreate,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user_from_token)):
    return await price_create_serv(sub, db)
