from app.schemas.subscriptions import SubscriptionCreate

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscriptions import Subscription


async def subscription_create(sub: SubscriptionCreate,
                              user_id: int,
                              db: AsyncSession):
    sub_add = Subscription(
        user_id=user_id,
        token=sub.token,
        threshold=sub.threshold,
        comment=sub.comment
    )
    db.add(sub_add)
    await db.commit()
    await db.refresh(sub_add)
    return sub_add
