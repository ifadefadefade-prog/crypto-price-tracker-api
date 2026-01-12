from app.crud.prices import create_price as create_price_crud
from app.schemas.prices import PriceResponse
from app.models.prices import Price
from app.crud.token import get_token_from_db
from app.services.price_sources import get_cex_price, get_dex_price
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
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

    if price_dex is None or price_cex is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Ошибка в получении цены")
    price_dex = float(price_dex)
    price_cex = float(price_cex)
    spread = abs(price_dex - price_cex) / price_cex * 100

    orm_price = Price(
        token_id=token.id,
        price_dex=price_dex,
        price_cex=price_cex,
        spread=spread
    )
    db_price = await create_price_crud(db, orm_price)
    return PriceResponse(
            id=db_price.id,
            token=token.symbol,
            price_dex=price_dex,
            price_cex=price_cex,
            spread=spread,
            timestamp=(db_price.timestamp if hasattr(db_price, 'timestamp')
                       else datetime.now()))
