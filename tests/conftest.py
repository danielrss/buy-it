import pytest

from app.config import Settings, get_settings


@pytest.fixture
def settings() -> Settings:
    get_settings.cache_clear()
    return get_settings()
