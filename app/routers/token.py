from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.token import TokenCreate, TokenDelete
from app.services.token import add_token, delete_token, get_token

from app.dependencies import get_session, get_current_user_from_token

from app.models.users import User


router = APIRouter(prefix="/token", tags=["token"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_token_rout(
        data: TokenCreate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user_from_token)):
    return await add_token(session, data)


@router.get("/{value}", status_code=status.HTTP_200_OK)
async def get_token_by_value(value: str,
                             session: AsyncSession = Depends(get_session)):
    return await get_token(session, value)


@router.delete("/{value}", status_code=status.HTTP_200_OK)
async def delete_token_rout(
        value: TokenDelete,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user_from_token)):
    return await delete_token(session, value)
