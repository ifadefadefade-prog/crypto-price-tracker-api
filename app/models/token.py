from __future__ import annotations
from sqlalchemy.orm import relationship
from sqlalchemy.types import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from sqlalchemy import ForeignKey
from datetime import datetime


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    symbol: Mapped[str] = mapped_column(String(25), index=True)
    chain: Mapped[str] = mapped_column(String(20), index=True)
    address: Mapped[str] = mapped_column(String(64), index=True)
    cex_symbol: Mapped[str] = mapped_column(String(20), index=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(), index=True)

    user: Mapped["User"] = relationship(back_populates="tokens")

    prices: Mapped[list["Price"]] = relationship(
        back_populates="token",
        cascade="all, delete-orphan"
    )
