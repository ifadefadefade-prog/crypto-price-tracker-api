from app.crud.prices import create_price as create_price_crud
from app.schemas.prices import PriceResponse
from app.models.prices import Price
from app.crud.token import get_token_from_db
from app.services.price_sources import get_cex_price, get_dex_price
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import aiohttp


async def create_price_service(db: AsyncSession,
                               value: str):
    token = await get_token_from_db(db, value)
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Token not found")
    async with aiohttp.ClientSession() as session:
        price_dex = await get_dex_price(session, token.address)
        price_cex = await get_cex_price(session, token.cex_symbol)

    spread = abs(price_dex - price_cex) / price_cex * 100

    orm_price = Price(
        token_id=token.id,
        price_dex=price_dex,
        price_cex=price_cex,
        spread=spread
    )
    db_price = await create_price_crud(db, orm_price)
    return PriceResponse.model_validate(db_price)
