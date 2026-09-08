import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection, make_url
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.database import Base
from app.models import *  # noqa: F401, F403 — import all models
from app.config import get_settings

config = context.config
settings = get_settings()

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    # asyncpg versions without channel_binding support reject Neon's
    # channel_binding query parameter before a connection is even attempted.
    # Remove it here; TLS is enabled explicitly for the production database.
    db_url = make_url(settings.DATABASE_URL)
    connect_args = {}

    if db_url.drivername == "postgresql+asyncpg":
        query = dict(db_url.query)
        query.pop("channel_binding", None)
        db_url = db_url.set(query=query)
        if settings.ENVIRONMENT.lower() == "production":
            connect_args["ssl"] = "require"

    connectable = async_engine_from_config(
        {"sqlalchemy.url": str(db_url)},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
