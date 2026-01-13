from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.token import Token

from typing import Optional, List
from datetime import datetime

MAX_LIMIT = 100


async def get_tokens_for_filter(
        db: AsyncSession,
        *,
        user_ids: Optional[List[int]] = None,
        symbols: Optional[List[str]] = None,
        chains: Optional[List[str]] = None,
        cex_symbols: Optional[List[str]] = None,
        addresses: Optional[List[str]] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0):

    stmt = select(Token)

    if user_ids:
        stmt = stmt.where(Token.user_id.in_(user_ids))

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

    limit = min(limit, MAX_LIMIT)
    stmt = stmt.limit(limit).offset(offset)
    result = await db.execute(stmt)
    return result.scalars().all()
