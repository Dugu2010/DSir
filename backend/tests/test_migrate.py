import pytest

from app.migrate import LEGACY_REQUIRED_TABLES, _validate_existing_schema


def test_rejects_incomplete_existing_schema_with_users_table():
    with pytest.raises(RuntimeError, match="not a complete DSir database"):
        _validate_existing_schema({"users", "alembic_version"})


def test_accepts_complete_legacy_dsir_schema():
    _validate_existing_schema(LEGACY_REQUIRED_TABLES)


def test_empty_database_can_start_from_initial_migration():
    _validate_existing_schema(set())
