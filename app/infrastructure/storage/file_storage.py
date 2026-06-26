from abc import ABC, abstractmethod
from enum import StrEnum

from app.infrastructure.storage.errors import FileTooLarge, UnsupportedFileType


class ContentType(StrEnum):
    JPEG = "image/jpeg"
    PNG = "image/png"
    WEBP = "image/webp"


EXTENSIONS: dict[ContentType, list[str]] = {
    ContentType.JPEG: [".jpg", ".jpeg"],
    ContentType.PNG: [".png"],
    ContentType.WEBP: [".webp"],
}

IMAGE_CONTENT_TYPES = {ContentType.JPEG, ContentType.PNG, ContentType.WEBP}


class FileStorage(ABC):
    async def save(
        self,
        data: bytes,
        path: str,
        content_type: ContentType | None = None,
        max_bytes: int | None = None,
    ) -> str:
        if max_bytes is not None and len(data) > max_bytes:
            raise FileTooLarge
        if content_type is not None:
            if not self.matches_signature(data, content_type):
                raise UnsupportedFileType
            path += EXTENSIONS[content_type][0]
        return await self._write(data, path)

    @staticmethod
    def matches_signature(data: bytes, content_type: ContentType) -> bool:
        if content_type is ContentType.JPEG:
            return data[:3] == b"\xff\xd8\xff"
        if content_type is ContentType.PNG:
            return data[:8] == b"\x89PNG\r\n\x1a\n"
        if content_type is ContentType.WEBP:
            return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
        return False

    @abstractmethod
    async def _write(self, data: bytes, path: str) -> str: ...
