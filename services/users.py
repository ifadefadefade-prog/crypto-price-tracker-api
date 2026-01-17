from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.crud.users import (
    create_user, get_user_by_id,
    get_user_by_login, set_user_password
)
from app.crud.users import delete_user as delete_user_crud
from app.security import get_password_hash, verify_password
from app.models.users import User

from app.dependencies import create_access_token
from app.schemas.users import UserResponse


async def register_user_service(db, user_data):
    user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password)
    )

    try:
        return await create_user(user, db)

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )


async def login_user(user_data, db):
    user = await get_user_by_login(user_data.login, db)
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials")
    access_token = create_access_token(
        data={"sub": str(user.id)}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


async def update_user_pass(user_data, user_id, db):
    user = await get_user_by_id(db, user_id)
    if not user or not verify_password:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found"
                            )
    if not verify_password(user_data.old_pass, user.password_hash):
        raise HTTPException(401, detail="Wrong password")

    res = await set_user_password(db, user,
                                  get_password_hash(user_data.new_pass))
    if not res:
        raise HTTPException(401, detail="Wrong password")
    return UserResponse.model_validate(res)


async def delete_user(user_id, db):
    user_obj = await get_user_by_id(db, user_id)
    if not user_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return await delete_user_crud(user_obj, db)
