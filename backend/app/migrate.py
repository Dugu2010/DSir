"""Safely run Alembic migrations for fresh and legacy DSir databases.

Older deployments created their schema with SQLAlchemy ``create_all`` and did
not record an Alembic revision. When that legacy schema is detected, adopt it
at the last revision before the new additive migrations, then upgrade normally.
Fresh databases still run the full migration chain from the beginning.
"""

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url
from sqlalchemy.pool import NullPool

from app.config import get_settings


LEGACY_BASELINE_REVISION = "0007_python_lesson_1_interactive"


def _sync_database_url(database_url: str, environment: str) -> str:
    url = make_url(database_url)
    if url.drivername in {"postgres", "postgresql", "postgresql+asyncpg"}:
        query = dict(url.query)
        query.pop("channel_binding", None)
        if environment.lower() == "production":
            query.setdefault("sslmode", "require")
        url = url.set(drivername="postgresql+psycopg", query=query)
    return url.render_as_string(hide_password=False)


def _adopt_legacy_schema(config: Config) -> bool:
    settings = get_settings()
    engine = create_engine(
        _sync_database_url(settings.DATABASE_URL, settings.ENVIRONMENT),
        poolclass=NullPool,
    )
    try:
        with engine.connect() as connection:
            inspector = inspect(connection)
            has_users = inspector.has_table("users")
            has_alembic_version = inspector.has_table("alembic_version")
            has_revision = False
            if has_alembic_version:
                has_revision = connection.execute(
                    text("SELECT EXISTS (SELECT 1 FROM alembic_version)")
                ).scalar_one()

        if has_users and not has_revision:
            print(
                "Existing DSir schema has no Alembic history; adopting it at "
                f"{LEGACY_BASELINE_REVISION}."
            )
            command.stamp(config, LEGACY_BASELINE_REVISION)
            return True
        return False
    finally:
        engine.dispose()


def main() -> None:
    config = Config("alembic.ini")
    _adopt_legacy_schema(config)
    command.upgrade(config, "head")


if __name__ == "__main__":
    main()
