import asyncio
from pathlib import Path

from app.infrastructure.storage.file_storage import FileStorage


class LocalFileStorage(FileStorage):
    def __init__(self, root: Path, url_prefix: str) -> None:
        self._root = root
        self._url_prefix = url_prefix

    async def _write(self, data: bytes, path: str) -> str:
        dest = self._root / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(dest.write_bytes, data)
        return f"{self._url_prefix}/{path}"
