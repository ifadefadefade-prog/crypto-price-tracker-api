from app.crud.prices import create_price as create_price_crud
from app.models.prices import Price
from app.crud.token import get_token_from_db
from app.crud.token import get_token_from_db_for_id
from app.services.price_sources import get_cex_price, get_dex_price
from app.dependencies import async_session
import aiohttp


class TokenNotFound(Exception):
    pass


class PriceSourceError(Exception):
    pass


async def create_price_service(value: str) -> Price:
    async with async_session() as db:
        token = await get_token_from_db(db, value)
        if not token:
            raise TokenNotFound()

        async with aiohttp.ClientSession() as session:
            price_dex = await get_dex_price(session, token.address)
            price_cex = await get_cex_price(session, token.cex_symbol)

        if price_dex is None or price_cex is None:
            raise PriceSourceError()

        price_dex = float(price_dex)
        price_cex = float(price_cex)
        spread = abs(price_dex - price_cex) / price_cex * 100

        orm_price = Price(
            token_id=token.id,
            price_dex=price_dex,
            price_cex=price_cex,
            spread=spread,
        )

        return await create_price_crud(db, orm_price)


async def create_price_service_for_celery(session,
                                          token_id: int) -> Price:
    async with async_session() as db:
        token = await get_token_from_db_for_id(db, token_id)
        if not token:
            raise TokenNotFound()

        price_dex = await get_dex_price(session, token.address)
        price_cex = await get_cex_price(session, token.cex_symbol)

        if price_dex is None or price_cex is None:
            raise PriceSourceError()

        price_dex = float(price_dex)
        price_cex = float(price_cex)
        spread = abs(price_dex - price_cex) / price_cex * 100

        orm_price = Price(
            token_id=token.id,
            price_dex=price_dex,
            price_cex=price_cex,
            spread=spread,
        )

        return await create_price_crud(db, orm_price)
