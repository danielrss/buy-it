from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.deps import get_db_session


def _fake_session(raises: bool = False):
    mock = AsyncMock()
    if raises:
        mock.execute.side_effect = Exception("DB down")

    async def _override() -> AsyncGenerator:
        yield mock

    return _override


@pytest.mark.integration
class TestDbHealth:
    async def test_returns_200_when_db_is_up(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        app.dependency_overrides[get_db_session] = _fake_session(raises=False)
        try:
            response = await client.get("/health/db")
        finally:
            app.dependency_overrides.clear()
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    async def test_returns_503_when_db_is_down(
        self, app: FastAPI, client: AsyncClient
    ) -> None:
        app.dependency_overrides[get_db_session] = _fake_session(raises=True)
        try:
            response = await client.get("/health/db")
        finally:
            app.dependency_overrides.clear()
        assert response.status_code == 503
