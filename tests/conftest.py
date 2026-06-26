import pytest

from app.config import MediaSettings, Settings, get_media_settings, get_settings


@pytest.fixture
def settings() -> Settings:
    get_settings.cache_clear()
    return get_settings()


@pytest.fixture
def media_settings() -> MediaSettings:
    get_media_settings.cache_clear()
    return get_media_settings()
