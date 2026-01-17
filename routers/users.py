from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.users import UserCreate, UserLogin
from app.schemas.users import UserChangePassword, UserResponse
from app.schemas.auth import Token

from app.services.users import delete_user as delete_user_serv
from app.services.users import (
    register_user_service,
    update_user_pass, login_user
)

from app.dependencies import get_session, get_current_user_from_token

from app.models.users import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse,
             status_code=status.HTTP_201_CREATED)
async def create_user(
        data: UserCreate,
        session: AsyncSession = Depends(get_session)):
    user_add = await register_user_service(session, user_data=data)
    return UserResponse.model_validate(user_add)


@router.post("/login", status_code=status.HTTP_200_OK,
             response_model=Token)
async def user_login(
        data: UserLogin,
        session: AsyncSession = Depends(get_session)):
    return await login_user(data, session)


@router.put("/", status_code=status.HTTP_202_ACCEPTED,
            response_model=UserResponse)
async def update_pass(
        data: UserChangePassword,
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user_from_token)):
    return await update_user_pass(data, current_user.id, session)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        session: AsyncSession = Depends(get_session),
        current_user: User = Depends(get_current_user_from_token)):
    await delete_user_serv(current_user.id, session)
