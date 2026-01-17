from app.crud.token import get_token_from_db
from app.crud.admin.token import get_tokens_for_filter
from app.schemas.token import TokenResponse
from app.models.token import Token
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from typing import Optional, List

from datetime import datetime


async def delete_token_admin(
        db: AsyncSession,
        value: str):
    token = await get_token_from_db(db, value)

    if not token:
        raise HTTPException(404, "Token not found")

    await db.delete(token)
    await db.commit()
    return {"detail": "Token deleted"}


async def get_token_admin(db: AsyncSession, value: str):
    stmt = select(Token).where(
        (Token.symbol == value) |
        (Token.address == value) |
        (Token.cex_symbol == value)
    )
    result = await db.execute(stmt)
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(404, "Token not found")
    return TokenResponse.model_validate(token)


async def get_list_tokens(
        db: AsyncSession,
        user_ids: Optional[List[int]] = None,
        symbols: Optional[List[str]] = None,
        chains: Optional[List[str]] = None,
        cex_symbols: Optional[List[str]] = None,
        addresses: Optional[List[str]] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0) -> list[TokenResponse]:
    tokens = await get_tokens_for_filter(
        db=db,
        user_ids=user_ids,
        symbols=symbols,
        chains=chains,
        cex_symbols=cex_symbols,
        addresses=addresses,
        created_after=created_after,
        created_before=created_before,
        limit=limit,
        offset=offset,)
    return [TokenResponse.model_validate(t) for t in tokens]
