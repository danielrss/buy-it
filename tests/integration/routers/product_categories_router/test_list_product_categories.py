import pytest
from httpx import AsyncClient

BASE = "/v1/product-categories"


@pytest.mark.integration
class TestListProductCategories:
    async def test_list_returns_empty_list(self, client: AsyncClient) -> None:
        resp = await client.get(BASE)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_contains_created_categories(self, client: AsyncClient) -> None:
        await client.post(BASE, json={"name": "Alpha", "parent_category_id": None})
        await client.post(BASE, json={"name": "Beta", "parent_category_id": None})
        resp = await client.get(BASE)
        assert resp.status_code == 200
        names = {c["name"] for c in resp.json()}
        assert {"Alpha", "Beta"}.issubset(names)
