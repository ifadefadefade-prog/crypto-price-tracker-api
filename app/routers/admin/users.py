from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.users import UserChangePassword, UserResponse
from app.db.base import UserRole
from app.dependencies import require_role

from app.services.users import delete_user as delete_user_serv
from app.services.users import (
    update_user_pass
)

from app.dependencies import get_session


router = APIRouter(
    prefix="/admin/users",
    tags=["admin-users"],
    dependencies=[Depends(require_role(UserRole.admin))]
)


@router.put("/", status_code=status.HTTP_202_ACCEPTED,
            response_model=UserResponse)
async def update_pass(
        data: UserChangePassword,
        user_id: int,
        session: AsyncSession = Depends(get_session)):
    return await update_user_pass(data, user_id, session)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int,
        session: AsyncSession = Depends(get_session)):
    await delete_user_serv(user_id, session)
