import pytest

from app.services.utils import to_absolute_media_url, to_relative_media_url

_REL = "/media/products/abc.png"
_BASE = "https://api.example.com"
_ABS = "https://api.example.com/media/products/abc.png"


@pytest.mark.unit
class TestToAbsoluteMediaUrl:
    def test_prepends_base_url(self) -> None:
        assert to_absolute_media_url(_REL, _BASE) == _ABS

    def test_strips_trailing_slash_on_base(self) -> None:
        assert to_absolute_media_url(_REL, _BASE + "/") == _ABS

    def test_empty_base_returns_relative(self) -> None:
        assert to_absolute_media_url(_REL, "") == _REL

    def test_none_image_returns_none(self) -> None:
        assert to_absolute_media_url(None, _BASE) is None


@pytest.mark.unit
class TestToRelativeMediaUrl:
    def test_strips_base_url(self) -> None:
        assert to_relative_media_url(_ABS, _BASE) == _REL

    def test_strips_trailing_slash_on_base(self) -> None:
        assert to_relative_media_url(_ABS, _BASE + "/") == _REL

    def test_relative_path_raises(self) -> None:
        # A bare relative path lacks the required base prefix.
        with pytest.raises(ValueError):
            to_relative_media_url(_REL, _BASE)

    def test_empty_base_returns_value_unchanged(self) -> None:
        assert to_relative_media_url(_ABS, "") == _ABS

    def test_none_image_returns_none(self) -> None:
        assert to_relative_media_url(None, _BASE) is None

    def test_foreign_host_raises(self) -> None:
        other = "https://cdn.other.com/media/products/abc.png"
        with pytest.raises(ValueError):
            to_relative_media_url(other, _BASE)
