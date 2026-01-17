from app.schemas.token import TokenCreate

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.token import Token

from typing import Optional, List

from datetime import datetime


MAX_LIMIT = 100


async def add_token_to_db(db: AsyncSession,
                          data_token: TokenCreate,
                          user_id: int) -> Token:
    token_add = Token(
        user_id=user_id,
        symbol=data_token.symbol,
        chain=data_token.chain,
        address=data_token.address,
        cex_symbol=data_token.cex_symbol)
    db.add(token_add)
    await db.commit()
    await db.refresh(token_add)
    return token_add


async def get_token_from_db(db: AsyncSession,
                            value: str,):
    stmt = select(Token).where((Token.symbol == value) |
                               (Token.address == value) |
                               (Token.cex_symbol == value))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_token_from_db_for_id(db: AsyncSession,
                                   token_id: int,):
    stmt = select(Token).where((Token.id == token_id))
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


async def get_tokens_for_filter(
        db: AsyncSession,
        user_id: int,
        symbols: Optional[List[str]] = None,
        chains: Optional[List[str]] = None,
        cex_symbols: Optional[List[str]] = None,
        addresses: Optional[List[str]] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0):
    stmt = select(Token).where(Token.user_id == user_id)

    if symbols:
        stmt = stmt.where(Token.symbol.in_(symbols))

    if chains:
        stmt = stmt.where(Token.chain.in_(chains))

    if cex_symbols:
        stmt = stmt.where(Token.cex_symbol.in_(cex_symbols))

    if addresses:
        stmt = stmt.where(Token.address.in_(addresses))

    if created_after:
        stmt = stmt.where(Token.created_at >= created_after)

    if created_before:
        stmt = stmt.where(Token.created_at <= created_before)

    stmt = (
        stmt
        .order_by(Token.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.execute(stmt)
    return result.scalars().all()
