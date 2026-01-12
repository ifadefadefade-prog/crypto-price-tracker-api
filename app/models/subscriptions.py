from __future__ import annotations
from sqlalchemy.types import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import sqlalchemy as sa
from app.db.base import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, sa.ForeignKey("users.id", ondelete="CASCADE"),
                                         nullable=False, index=True)
    token: Mapped[str] = mapped_column(String(15), nullable=False, index=True)
    threshold: Mapped[float] = mapped_column(Float, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(), index=True)
    user: Mapped["User"] = relationship("User", back_populates="subscriptions",
                                        lazy="selectin")