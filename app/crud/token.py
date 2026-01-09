from app.schemas.token import TokenCreate

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.token import Token


async def add_token_to_db(db: AsyncSession,
                          data_token: TokenCreate):
    token_add = Token(
        symbol=data_token.symbol,
        chain=data_token.chain,
        address=data_token.address,
        cex_symbol=data_token.cex_symbol)
    db.add(token_add)
    await db.commit()
    await db.refresh(token_add)
    return token_add


async def get_token_from_db(db: AsyncSession,
                            value: str):
    stmt = select(Token).where((Token.symbol == value) |
                               (Token.address == value) |
                               (Token.cex_symbol == value))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def delete_token_from_db(db: AsyncSession,
                               value: str):
    token = await get_token_from_db(db, value)
    if not token:
        return False
    await db.delete(token)
    await db.commit()
    return True
