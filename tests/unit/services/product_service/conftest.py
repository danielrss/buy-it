import pytest

from app.config import MediaSettings


@pytest.fixture
def media_settings() -> MediaSettings:
    """A MediaSettings to inject into ProductService under test."""
    return MediaSettings(media_base_url="https://api.example.com")
