from sqlalchemy.types import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Enum
from app.db.base import Source
from datetime import datetime, timezone
from sqlalchemy.orm import validates
import sqlalchemy as sa
from app.db.base import Base


class Price(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True,
                                    autoincrement=True)
    token: Mapped[str] = mapped_column(String(15), nullable=False, index=True)
    price: Mapped[float] = mapped_column(
                                        Float,
                                        sa.CheckConstraint("price > 0"),
                                        nullable=False)
    source: Mapped[Source] = mapped_column(Enum(Source, name="price_source"),
                                           nullable=False)
    spread: Mapped[float | None] = mapped_column(Float, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    @validates("price")
    def validate_price(self, key, value):
        if value <= 0:
            raise ValueError("Price must be positive")
        return value

    def __repr__(self) -> str:
        return f"<Price {self.token} {self.price} ({self.source})>"
