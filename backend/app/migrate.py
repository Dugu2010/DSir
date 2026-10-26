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
LEGACY_REQUIRED_TABLES = {"users", "courses", "modules", "lessons", "quizzes", "quiz_attempts"}


def _validate_existing_schema(tables: set[str]) -> None:
    """Reject a database with a colliding but incomplete ``users`` table."""
    missing_tables = LEGACY_REQUIRED_TABLES - tables
    if "users" in tables and missing_tables:
        missing = ", ".join(sorted(missing_tables))
        raise RuntimeError(
            "DATABASE_URL points to an existing schema that is not a complete "
            f"DSir database (missing: {missing}). Refusing to migrate it; "
            "configure the service with the DSir PostgreSQL database."
        )


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
            tables = set(inspector.get_table_names())
            has_alembic_version = "alembic_version" in tables
            revisions = []
            if has_alembic_version:
                revisions = connection.execute(
                    text("SELECT version_num FROM alembic_version")
                ).scalars().all()

        # A legacy DSir database was created from the ORM and already contains
        # the core application tables. Never stamp a partial or unrelated
        # database merely because it happens to have a table named ``users``.
        _validate_existing_schema(tables)

        if "users" in tables and not revisions:
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
