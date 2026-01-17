from app.crud.subscriptions import subscription_create as subscription_create_crud
from app.schemas.subscriptions import SubscriptionResponse
from fastapi import HTTPException, status


async def subscription_create(sub_data, user_id, db):
    res = await subscription_create_crud(sub_data, user_id, db)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Subscription not created"
        )
    return SubscriptionResponse.model_validate(res)
