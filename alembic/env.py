from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.db.base import Base
from app.core.config import settings

# импорт моделей (ОБЯЗАТЕЛЬНО)
from app.models.users import User
from app.models.token import Token
from app.models.prices import Price
from app.models.subscriptions import Subscription

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_sync_database_url() -> str:
    """
    Превращаем async URL в sync для Alembic
    """
    return settings.DATABASE_URL.replace(
        "postgresql+asyncpg",
        "postgresql+psycopg2"
    )


def run_migrations_online():
    connectable = engine_from_config(
        {
            **config.get_section(config.config_ini_section),
            "sqlalchemy.url": get_sync_database_url(),
        },
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
