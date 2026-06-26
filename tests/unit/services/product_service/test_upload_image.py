import uuid
from unittest.mock import AsyncMock

import pytest

from app.infrastructure.storage.file_storage import (
    ContentType,
    FileStorage,
    FileTooLarge,
    UnsupportedFileType,
)
from app.services.errors import ImageTooLarge, InvalidImageType
from app.services.product_service import ProductService

_PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
_MAX = 1024 * 1024


def _upload_file(data: bytes, content_type: str | None):  # type: ignore[no-untyped-def]
    f = AsyncMock()
    f.content_type = content_type

    async def _read(size: int = -1) -> bytes:
        return data[:size] if size >= 0 else data

    f.read = _read
    return f


class _RecordingStorage(FileStorage):
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def save(self, data, path, content_type=None, max_bytes=None) -> str:  # type: ignore[no-untyped-def]
        self.calls.append(
            {
                "data": data,
                "path": path,
                "content_type": content_type,
                "max_bytes": max_bytes,
            }
        )
        return "/media/products/stub.png"

    async def _write(self, data: bytes, path: str) -> str:
        raise NotImplementedError


class _RaisingStorage(FileStorage):
    def __init__(self, exc: Exception) -> None:
        self._exc = exc

    async def save(self, data, path, content_type=None, max_bytes=None) -> str:  # type: ignore[no-untyped-def]
        raise self._exc

    async def _write(self, data: bytes, path: str) -> str:
        raise NotImplementedError


def _service(storage: FileStorage) -> ProductService:
    return ProductService(session=AsyncMock(), storage=storage, max_image_bytes=_MAX)


@pytest.mark.unit
class TestUploadImage:
    async def test_returns_url_from_storage(self) -> None:
        storage = _RecordingStorage()
        result = await _service(storage).upload_image(_upload_file(_PNG, "image/png"))
        assert result == "/media/products/stub.png"

    async def test_builds_products_path_with_uuid_name(self) -> None:
        storage = _RecordingStorage()
        await _service(storage).upload_image(_upload_file(_PNG, "image/png"))
        path = storage.calls[0]["path"]
        assert path.startswith("products/")
        # name is a bare uuid4; the storage layer appends the extension
        uuid.UUID(path.removeprefix("products/"))

    async def test_delegates_content_type_and_max_bytes(self) -> None:
        storage = _RecordingStorage()
        await _service(storage).upload_image(_upload_file(_PNG, "image/png"))
        call = storage.calls[0]
        assert call["content_type"] is ContentType.PNG
        assert call["max_bytes"] == _MAX
        assert call["data"] == _PNG

    async def test_unknown_content_type_raises_without_calling_storage(self) -> None:
        storage = _RecordingStorage()
        with pytest.raises(InvalidImageType):
            await _service(storage).upload_image(_upload_file(_PNG, "image/gif"))
        assert storage.calls == []

    async def test_missing_content_type_raises(self) -> None:
        storage = _RecordingStorage()
        with pytest.raises(InvalidImageType):
            await _service(storage).upload_image(_upload_file(_PNG, None))
        assert storage.calls == []

    async def test_unsupported_file_type_translated(self) -> None:
        storage = _RaisingStorage(UnsupportedFileType())
        with pytest.raises(InvalidImageType):
            await _service(storage).upload_image(_upload_file(_PNG, "image/png"))

    async def test_file_too_large_translated(self) -> None:
        storage = _RaisingStorage(FileTooLarge())
        with pytest.raises(ImageTooLarge):
            await _service(storage).upload_image(_upload_file(_PNG, "image/png"))

    async def test_no_storage_raises_runtime_error(self) -> None:
        service = ProductService(session=AsyncMock(), storage=None)
        with pytest.raises(RuntimeError):
            await service.upload_image(_upload_file(_PNG, "image/png"))
