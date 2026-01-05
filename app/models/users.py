from __future__ import annotations
from sqlalchemy.types import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy import Enum
from datetime import datetime, timezone
from app.db.base import Base
from app.db.base import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    username: Mapped[str] = mapped_column(String(20), nullable=False,
                                          index=True, unique=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False,
                                       unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"),
                                           nullable=False,
                                           default=UserRole.user)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    subscriptions: Mapped[list["Subscription"]] = relationship(back_populates="user",
                                                               cascade="all, delete-orphan")
