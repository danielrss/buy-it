import uuid

import pytest
from httpx import AsyncClient

BASE = "/v1/product-categories"


@pytest.mark.integration
class TestGetProductCategory:
    async def test_get_returns_200(self, client: AsyncClient) -> None:
        created = (await client.post(BASE, json={"name": "GetMe"})).json()
        resp = await client.get(f"{BASE}/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    async def test_get_unknown_returns_404(self, client: AsyncClient) -> None:
        resp = await client.get(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_list_contains_created_categories(self, client: AsyncClient) -> None:
        await client.post(BASE, json={"name": "Alpha"})
        await client.post(BASE, json={"name": "Beta"})
        resp = await client.get(BASE)
        assert resp.status_code == 200
        names = {c["name"] for c in resp.json()}
        assert {"Alpha", "Beta"}.issubset(names)
