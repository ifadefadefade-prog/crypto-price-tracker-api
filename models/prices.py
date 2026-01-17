from sqlalchemy.types import Float
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone
import sqlalchemy as sa
from app.db.base import Base
from sqlalchemy.orm import relationship


class Price(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(primary_key=True)
    token_id: Mapped[int] = mapped_column(
        sa.ForeignKey("tokens.id", ondelete="CASCADE"),
        index=True
    )

    price_dex: Mapped[float] = mapped_column(
        Float,
        sa.CheckConstraint("price_dex > 0"),
        nullable=False
    )
    price_cex: Mapped[float] = mapped_column(
        Float,
        sa.CheckConstraint("price_cex > 0"),
        nullable=False
    )

    spread: Mapped[float | None] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(),
        index=True
    )

    token: Mapped["Token"] = relationship(
        back_populates="prices",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        token_symbol = self.token.symbol if self.token else self.token_id
        return (
            f"<Price token={token_symbol} "
            f"dex={self.price_dex} "
            f"cex={self.price_cex} "
            f"spread={self.spread:.2f}%>"
        )
