
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "add_tokens_with_user_id"
down_revision: Union[str, Sequence[str], None] = "4a7df50bb2f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tokens",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("symbol", sa.String(25), nullable=False),
        sa.Column("chain", sa.String(20), nullable=False),
        sa.Column("address", sa.String(64), nullable=False),
        sa.Column("cex_symbol", sa.String(20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    op.create_index("uq_tokens_user_created_at", "tokens",
                    ["created_at"])

    op.create_index(
        "uq_tokens_user_symbol",
        "tokens",
        ["user_id", "symbol"],
        unique=True,
    )

    op.create_index(
        "uq_tokens_user_address",
        "tokens",
        ["user_id", "address"],
        unique=True,
    )

    op.create_index(
        "uq_tokens_user_cex_symbol",
        "tokens",
        ["user_id", "cex_symbol"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_table("tokens")
