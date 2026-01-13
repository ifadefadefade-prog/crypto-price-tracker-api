from fastapi import APIRouter, Depends, status, Query
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.token import TokenCreate, TokenResponse
from app.services.token import add_token, delete_token, get_token
from app.services.token import get_list_tokens

from app.dependencies import get_session, get_current_user_from_token

from app.models.users import User


router = APIRouter(prefix="/token", tags=["token"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def add_token_rout(
        data: TokenCreate,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user_from_token)):
    return await add_token(session, data, current_user.id)


@router.get("/{value}", status_code=status.HTTP_200_OK)
async def get_token_by_value(
        value: str,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user_from_token)):
    return await get_token(session, value, current_user.id)


@router.delete("/{value}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_token_route(
    value: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user_from_token)
):
    await delete_token(session, value, current_user.id)
    return {"detail": "Token deleted"}


@router.get("/", response_model=List[TokenResponse],
            status_code=status.HTTP_200_OK)
async def get_my_tokens(
    symbols: Optional[List[str]] = Query(None),
    chains: Optional[List[str]] = Query(None),
    cex_symbols: Optional[List[str]] = Query(None),
    addresses: Optional[List[str]] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user_from_token)
):
    return await get_list_tokens(
        db=session,
        user_id=current_user.id,
        symbols=symbols,
        chains=chains,
        cex_symbols=cex_symbols,
        addresses=addresses,
        created_after=created_after,
        created_before=created_before
    )
