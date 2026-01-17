from pydantic import BaseModel, Field


class TokenBase(BaseModel):
    symbol: str = Field(max_length=25)
    chain: str = Field(max_length=20)
    address: str = Field(max_length=64)
    cex_symbol: str = Field(max_length=20)


class TokenCreate(TokenBase):
    pass


class TokenResponse(TokenBase):
    id: int

    class Config:
        from_attributes = True


class TokenDelete(BaseModel):
    value: str
