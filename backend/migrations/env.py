from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import make_url

from app.config import get_settings
from app.database import Base
from app.models import *  # noqa: F401,F403 — import all models

config = context.config
settings = get_settings()

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _migration_url():
    """Build a synchronous psycopg URL for Alembic.

    The application uses psycopg for PostgreSQL. Keeping Alembic on the same
    driver avoids asyncpg rejecting Neon connection parameters such as
    channel_binding before a connection is established.
    """
    db_url = make_url(settings.DATABASE_URL)

    if db_url.drivername in {"postgresql+asyncpg", "postgresql"}:
        query = dict(db_url.query)
        query.pop("channel_binding", None)
        if settings.ENVIRONMENT.lower() == "production":
            query.setdefault("sslmode", "require")
        db_url = db_url.set(drivername="postgresql+psycopg", query=query)

    return str(db_url)


def run_migrations_offline() -> None:
    url = _migration_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _migration_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
