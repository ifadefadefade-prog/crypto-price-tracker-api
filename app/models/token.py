from __future__ import annotations
from sqlalchemy.orm import relationship
from sqlalchemy.types import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    symbol: Mapped[str] = mapped_column(String(25), unique=True, index=True)
    chain: Mapped[str] = mapped_column(String(20), index=True)
    address: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    cex_symbol: Mapped[str] = mapped_column(String(20), unique=True,
                                            index=True)
    prices: Mapped[list["Price"]] = relationship(
        back_populates="token",
        cascade="all, delete-orphan"
    )
