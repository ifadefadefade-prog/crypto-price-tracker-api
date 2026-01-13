from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.dependencies import require_role
from app.db.base import UserRole
from app.services.admin.token import get_list_tokens

from app.schemas.token import TokenResponse

from datetime import datetime

from typing import Optional, List

from app.services.admin.token import (
    delete_token_admin, get_token_admin
)

router = APIRouter(
    prefix="/admin/token",
    tags=["admin-token"],
    dependencies=[Depends(require_role(UserRole.admin))]
)


@router.get("/{value}", status_code=status.HTTP_200_OK)
async def get_token_by_value(
        value: str,
        session: AsyncSession = Depends(get_session)):
    return await get_token_admin(session, value)


@router.delete("/{value}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_token_route(
        value: str,
        session: AsyncSession = Depends(get_session)):
    await delete_token_admin(session, value)
    return {"detail": "Token deleted"}


@router.get("/", response_model=List[TokenResponse],
            status_code=status.HTTP_200_OK)
async def get_my_tokens(
        user_ids: Optional[List[int]] = Query(None),
        symbols: Optional[List[str]] = Query(None),
        chains: Optional[List[str]] = Query(None),
        cex_symbols: Optional[List[str]] = Query(None),
        addresses: Optional[List[str]] = Query(None),
        created_after: Optional[datetime] = Query(None),
        created_before: Optional[datetime] = Query(None),
        session: AsyncSession = Depends(get_session)):
    return await get_list_tokens(
        db=session,
        user_ids=user_ids,
        symbols=symbols,
        chains=chains,
        cex_symbols=cex_symbols,
        addresses=addresses,
        created_after=created_after,
        created_before=created_before
    )
