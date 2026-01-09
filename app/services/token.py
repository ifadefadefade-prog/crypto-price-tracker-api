from app.crud.token import add_token_to_db, get_token_from_db
from app.crud.token import delete_token_from_db
from app.schemas.token import TokenResponse, TokenCreate, TokenDelete
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


async def add_token(db: AsyncSession,
                    token_data: TokenCreate):
    try:
        token_add = await add_token_to_db(db, token_data)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Token already exists"
        )
    return TokenResponse.model_validate(token_add)


async def delete_token(db: AsyncSession,
                       token_data: TokenDelete):
    token_delete = await delete_token_from_db(db, token_data.value)
    if not token_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Token not found")
    return {"message": "Token delete success"}


async def get_token(db: AsyncSession,
                    value: str):
    token = await get_token_from_db(db, value)
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Token not found")
    return TokenResponse.model_validate(token)
