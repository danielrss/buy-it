from pathlib import Path

import pytest

from app.infrastructure.storage.file_storage import (
    EXTENSIONS,
    ContentType,
    FileTooLarge,
    UnsupportedFileType,
)
from app.infrastructure.storage.local_file_storage import LocalFileStorage

_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
_JPEG = b"\xff\xd8\xff" + b"\x00" * 100
_WEBP = b"RIFF\x00\x00\x00\x00WEBP" + b"\x00" * 100

_MAX = 1024 * 1024


def _storage(tmp_path: Path) -> LocalFileStorage:
    return LocalFileStorage(tmp_path / "media", "/media")


@pytest.mark.unit
class TestLocalFileStorageSave:
    def test_extension_mapping(self) -> None:
        assert EXTENSIONS[ContentType.JPEG] == [".jpg", ".jpeg"]
        assert EXTENSIONS[ContentType.PNG] == [".png"]
        assert EXTENSIONS[ContentType.WEBP] == [".webp"]

    def test_matches_signature(self) -> None:
        assert LocalFileStorage.matches_signature(_PNG, ContentType.PNG)
        assert LocalFileStorage.matches_signature(_JPEG, ContentType.JPEG)
        assert LocalFileStorage.matches_signature(_WEBP, ContentType.WEBP)
        assert not LocalFileStorage.matches_signature(_JPEG, ContentType.PNG)

    async def test_appends_extension_from_content_type(self, tmp_path: Path) -> None:
        url = await _storage(tmp_path).save(
            _PNG, "products/test", content_type=ContentType.PNG, max_bytes=_MAX
        )
        assert url == "/media/products/test.png"
        assert (tmp_path / "media" / "products" / "test.png").read_bytes() == _PNG

    async def test_appends_canonical_extension_for_jpeg(self, tmp_path: Path) -> None:
        url = await _storage(tmp_path).save(
            _JPEG, "products/test", content_type=ContentType.JPEG
        )
        assert url == "/media/products/test.jpg"

    async def test_creates_nested_directories(self, tmp_path: Path) -> None:
        url = await _storage(tmp_path).save(b"data", "products/a/b/file.bin")
        assert url == "/media/products/a/b/file.bin"
        assert (
            tmp_path / "media" / "products" / "a" / "b" / "file.bin"
        ).read_bytes() == b"data"

    async def test_magic_byte_mismatch_raises(self, tmp_path: Path) -> None:
        with pytest.raises(UnsupportedFileType):
            await _storage(tmp_path).save(
                _JPEG, "products/x", content_type=ContentType.PNG
            )

    async def test_oversized_raises(self, tmp_path: Path) -> None:
        big = _PNG + b"\x00" * _MAX
        with pytest.raises(FileTooLarge):
            await _storage(tmp_path).save(
                big, "products/x", content_type=ContentType.PNG, max_bytes=_MAX
            )

    async def test_exact_max_size_is_accepted(self, tmp_path: Path) -> None:
        data = _PNG + b"\x00" * (_MAX - len(_PNG))
        assert len(data) == _MAX
        url = await _storage(tmp_path).save(
            data, "products/x", content_type=ContentType.PNG, max_bytes=_MAX
        )
        assert url == "/media/products/x.png"

    async def test_without_content_type_skips_magic_validation(
        self, tmp_path: Path
    ) -> None:
        url = await _storage(tmp_path).save(b"anything", "products/x.bin")
        assert url == "/media/products/x.bin"
