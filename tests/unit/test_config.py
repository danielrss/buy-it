import pytest

from app.config import Settings


@pytest.mark.unit
class TestSettings:
    def test_defaults(self) -> None:
        s = Settings()
        assert s.environment == "local"

    def test_env_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ENVIRONMENT", "production")
        s = Settings()
        assert s.environment == "production"

    def test_database_url_default(self) -> None:
        s = Settings()
        assert s.database_url == "postgresql+asyncpg://buyit:buyit@db:5432/buyit"

    def test_database_url_reflects_overrides(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("POSTGRES_USER", "admin")
        monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
        monkeypatch.setenv("POSTGRES_DB", "mydb")
        s = Settings()
        assert "admin:secret" in s.database_url
        assert "mydb" in s.database_url
