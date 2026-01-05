from pydantic import BaseModel, Field, PositiveFloat
from app.db.base import Source
from datetime import datetime


class PriceBase(BaseModel):
    token: str = Field(max_length=15, description="The symbol of the" +
                       " cryptocurrency token",
                       pattern=r'^[A-Z]{3,5}$')


class PriceCreate(PriceBase):
    price: PositiveFloat = Field(..., description="The price of" +
                                 " the cryptocurrency")
    source: Source = Field(..., description="The source of the price data")


class PriceResponse(PriceBase):
    id: int = Field(..., description="The unique identifier" +
                    " of the price entry")
    spread: float = Field(..., description="The spread percentage" +
                          " of the price")
    timestamp: datetime = Field(..., description="The timestamp" +
                                " when the price was recorded")
    source: Source = Field(..., description="The source of the price data")

    @classmethod
    def calc_spread(cls, dex_price: float, cex_price: float) -> float:
        if cex_price == 0:
            return 0.0
        return abs(dex_price - cex_price) / cex_price * 100
