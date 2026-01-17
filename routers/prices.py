from fastapi import APIRouter, Depends, status

from app.services.prices import create_price_service
from app.schemas.prices import PriceResponse
from app.models.users import User

from app.dependencies import get_current_user_from_token


router = APIRouter(prefix="/prices", tags=["prices"])


@router.post("/fetch/{value}", status_code=status.HTTP_201_CREATED,
             response_model=PriceResponse)
async def create_price(
        value: str,
        current_user: User = Depends(get_current_user_from_token)):
    price = await create_price_service(value)
    return PriceResponse.model_validate(price)
