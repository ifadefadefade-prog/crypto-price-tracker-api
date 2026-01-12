"""init tables

Revision ID: 4a7df50bb2f2
Revises:
Create Date: 2026-01-09
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4a7df50bb2f2"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(20), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(128)),
        sa.Column(
            "role",
            sa.Enum("user", "admin", name="user_role"),
            nullable=False,
            server_default="user",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "prices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "token_id",
            sa.Integer,
            sa.ForeignKey("tokens.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("price_dex", sa.Float, nullable=False),
        sa.Column("price_cex", sa.Float, nullable=False),
        sa.Column("spread", sa.Float),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("price_dex > 0", name="ck_prices_price_dex"),
        sa.CheckConstraint("price_cex > 0", name="ck_prices_price_cex"),
    )
    op.create_index("ix_prices_token_id", "prices", ["token_id"])
    op.create_index("ix_prices_timestamp", "prices", ["timestamp"])

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token", sa.String(15), nullable=False),
        sa.Column("threshold", sa.Float, nullable=False),
        sa.Column("comment", sa.String(500)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_subscriptions_user_id", "subscriptions", ["user_id"])
    op.create_index("ix_subscriptions_token", "subscriptions", ["token"])
    op.create_index("ix_subscriptions_created_at", "subscriptions", ["created_at"])


def downgrade() -> None:
    op.drop_table("subscriptions")
    op.drop_table("prices")
    op.drop_table("tokens")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS user_role")
