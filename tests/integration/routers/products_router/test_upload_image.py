from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.config import get_settings
from app.main import create_app

BASE = "/v1/products/image"

_PNG_HEADER = b"\x89PNG\r\n\x1a\n"
_VALID_PNG = _PNG_HEADER + b"\x00" * 100


@pytest.fixture
def app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Generator[FastAPI]:
    monkeypatch.setenv("MEDIA_ROOT", str(tmp_path / "media"))
    get_settings.cache_clear()
    result = create_app()
    yield result
    get_settings.cache_clear()


@pytest.mark.integration
class TestUploadProductImage:
    async def test_valid_png_returns_201_with_url(self, client: AsyncClient) -> None:
        resp = await client.post(
            BASE,
            files={"file": ("photo.png", _VALID_PNG, "image/png")},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["image_url"].startswith("/media/products/")
        assert body["image_url"].endswith(".png")

    async def test_uploaded_file_is_served(self, client: AsyncClient) -> None:
        upload_resp = await client.post(
            BASE,
            files={"file": ("photo.png", _VALID_PNG, "image/png")},
        )
        assert upload_resp.status_code == 201
        url = upload_resp.json()["image_url"]

        get_resp = await client.get(url)
        assert get_resp.status_code == 200
        assert get_resp.content == _VALID_PNG

    async def test_unsupported_content_type_returns_415(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(
            BASE,
            files={"file": ("file.txt", b"hello world", "text/plain")},
        )
        assert resp.status_code == 415
        assert resp.json()["detail"] == "unsupported image type"

    async def test_gif_returns_415(self, client: AsyncClient) -> None:
        resp = await client.post(
            BASE,
            files={"file": ("anim.gif", b"GIF89a" + b"\x00" * 100, "image/gif")},
        )
        assert resp.status_code == 415

    async def test_spoofed_content_type_returns_415(self, client: AsyncClient) -> None:
        resp = await client.post(
            BASE,
            files={"file": ("photo.png", b"notapng" * 20, "image/png")},
        )
        assert resp.status_code == 415
        assert resp.json()["detail"] == "unsupported image type"

    async def test_oversized_file_returns_413(self, client: AsyncClient) -> None:
        big = _PNG_HEADER + b"\x00" * (1024 * 1024)
        resp = await client.post(
            BASE,
            files={"file": ("big.png", big, "image/png")},
        )
        assert resp.status_code == 413
        assert resp.json()["detail"] == "image too large"
