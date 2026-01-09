from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prices import Price


async def create_price(db: AsyncSession,
                       price: Price) -> Price:
    db.add(price)
    await db.commit()
    await db.refresh(price)
    return price
