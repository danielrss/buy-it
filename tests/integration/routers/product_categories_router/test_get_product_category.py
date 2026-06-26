import uuid

import pytest
from httpx import AsyncClient

BASE = "/v1/product-categories"


@pytest.mark.integration
class TestGetProductCategory:
    async def test_get_returns_200(self, client: AsyncClient) -> None:
        created = (
            await client.post(BASE, json={"name": "GetMe", "parent_category_id": None})
        ).json()
        resp = await client.get(f"{BASE}/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    async def test_get_unknown_returns_404(self, client: AsyncClient) -> None:
        resp = await client.get(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404
