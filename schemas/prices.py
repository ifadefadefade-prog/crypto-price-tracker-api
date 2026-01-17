from pydantic import BaseModel, Field, PositiveFloat, ConfigDict
from datetime import datetime


class PriceBase(BaseModel):
    token: str = Field(max_length=15, description="The symbol of the" +
                       " cryptocurrency token",
                       pattern=r'^[A-Z]{3,5}$')
    price_dex: PositiveFloat
    price_cex: PositiveFloat


class PriceCreate(PriceBase):
    pass


class PriceResponse(PriceBase):
    id: int = Field(..., description="The unique identifier" +
                    " of the price entry")
    token: str
    price_dex: float
    price_cex: float
    spread: float = Field(..., description="The spread percentage" +
                          " of the price")
    timestamp: datetime = Field(..., description="The timestamp" +
                                " when the price was recorded")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def calc_spread(cls, dex_price: float, cex_price: float) -> float:
        if cex_price == 0:
            return 0.0
        return abs(dex_price - cex_price) / cex_price * 100
