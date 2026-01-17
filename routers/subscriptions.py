from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.subscriptions import SubscriptionCreate
from app.services.subscriptions import subscription_create

from app.dependencies import get_session, get_current_user_from_token

from app.models.users import User


router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_subscriptions(
        data: SubscriptionCreate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user_from_token)):
    return await subscription_create(data, current_user.id, session)
