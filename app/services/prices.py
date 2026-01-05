from app.crud.prices import price_create as price_create_crud
from app.schemas.prices import PriceResponse


async def price_create(db, price_data):
    price_add = await price_create_crud(price_data, db)
    return PriceResponse.model_validate(price_add)
