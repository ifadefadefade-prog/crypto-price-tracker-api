from datetime import datetime
from typing import Optional, List, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.token import Token
from app.schemas.token import TokenCreate

MAX_LIMIT = 100


def add_token_to_db(
    db: Session,
    data_token: TokenCreate,
    user_id: int,
) -> Token:
    token = Token(
        user_id=user_id,
        symbol=data_token.symbol,
        chain=data_token.chain,
        address=data_token.address,
        cex_symbol=data_token.cex_symbol,
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def get_token_from_db(
    db: Session,
    value: str,
) -> Optional[Token]:
    stmt = select(Token).where(
        (Token.symbol == value)
        | (Token.address == value)
        | (Token.cex_symbol == value)
    )
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def get_token_from_db_for_id(
    db: Session,
    token_id: int,
) -> Optional[Token]:
    stmt = select(Token).where(Token.id == token_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def delete_token_from_db(
    db: Session,
    value: str,
) -> bool:
    token = get_token_from_db(db, value)
    if not token:
        return False

    db.delete(token)
    db.commit()
    return True


def get_tokens_for_filter(
    db: Session,
    user_id: int,
    symbols: Optional[List[str]] = None,
    chains: Optional[List[str]] = None,
    cex_symbols: Optional[List[str]] = None,
    addresses: Optional[List[str]] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Token]:
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
        stmt.order_by(Token.created_at.desc())
        .limit(min(limit, MAX_LIMIT))
        .offset(offset)
    )

    result = db.execute(stmt)
    return result.scalars().all()
