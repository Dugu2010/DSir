from app.config import Settings


def test_jwt_secret_environment_aliases(monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)
    monkeypatch.setenv("JWT_SECRET", "secret-from-render-settings")

    settings = Settings(_env_file=None)

    assert settings.JWT_SECRET_KEY == "secret-from-render-settings"
