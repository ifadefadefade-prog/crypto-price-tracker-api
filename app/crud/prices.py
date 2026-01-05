from app.schemas.prices import PriceCreate

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prices import Price


async def price_create(price: PriceCreate,
                       db: AsyncSession):
    price_add = Price(
        token=price.token,
        price=price.price,
        source=price.source
    )
    db.add(price_add)
    await db.commit()
    await db.refresh(price_add)
    return price_add
