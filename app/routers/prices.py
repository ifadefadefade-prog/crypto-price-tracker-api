from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.prices import create_price_service
from app.schemas.prices import PriceResponse
from app.models.users import User

from app.dependencies import get_session, get_current_user_from_token

router = APIRouter(prefix="/prices", tags=["prices"])


@router.post("/fetch/{value}", status_code=status.HTTP_201_CREATED,
             response_model=PriceResponse)
async def create_price(
        value: str,
        db: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user_from_token)):
    return await create_price_service(db, value)
