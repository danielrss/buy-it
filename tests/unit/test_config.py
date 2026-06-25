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
