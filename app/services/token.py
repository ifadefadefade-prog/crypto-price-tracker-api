from app.crud.token import add_token_to_db, get_tokens_for_filter
from app.schemas.token import TokenResponse, TokenCreate
from app.models.token import Token
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime


async def add_token(db: AsyncSession,
                    token_data: TokenCreate,
                    user_id: int):
    try:
        token_add = await add_token_to_db(db, token_data, user_id=user_id)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Token already exists"
        )
    return TokenResponse.model_validate(token_add)


async def delete_token(
        db: AsyncSession,
        value: str,
        current_user_id: int):
    stmt = select(Token).where(
        (Token.symbol == value) |
        (Token.address == value) |
        (Token.cex_symbol == value),
        Token.user_id == current_user_id
    )
    result = await db.execute(stmt)
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(404, "Token not found")

    await db.delete(token)
    await db.commit()
    return {"detail": "Token deleted"}


async def get_token(db: AsyncSession, value: str, current_user_id: int):
    stmt = select(Token).where(
        (Token.symbol == value) |
        (Token.address == value) |
        (Token.cex_symbol == value),
        Token.user_id == current_user_id
    )
    result = await db.execute(stmt)
    token = result.scalar_one_or_none()
    if not token:
        raise HTTPException(404, "Token not found")
    return TokenResponse.model_validate(token)


async def list_tokens(
    db: AsyncSession,
    user_id: int,
    symbols: Optional[List[str]] = None,
    chains: Optional[List[str]] = None,
    cex_symbols: Optional[List[str]] = None,
    addresses: Optional[List[str]] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None
) -> list[TokenResponse]:
    tokens = await get_tokens_for_filter(
        db, user_id, symbols, chains, cex_symbols, addresses,
        created_after, created_before)
    return [TokenResponse.model_validate(t) for t in tokens]
