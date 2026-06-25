import uuid

import pytest
from httpx import AsyncClient

BASE = "/v1/products"
CATEGORIES_BASE = "/v1/product-categories"


async def _create_category(client: AsyncClient, name: str = "Electronics") -> str:
    resp = await client.post(
        CATEGORIES_BASE, json={"name": name, "parent_category_id": None}
    )
    return resp.json()["id"]


async def _create_product(
    client: AsyncClient, cat_id: str, title: str = "Laptop", sku: str = "LAP-001"
) -> dict:
    resp = await client.post(
        BASE,
        json={
            "title": title,
            "description": None,
            "sku": sku,
            "price": "999.99",
            "image_url": None,
            "product_category_id": cat_id,
        },
    )
    return resp.json()


@pytest.mark.integration
class TestDeleteProduct:
    async def test_delete_returns_204(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client)
        created = await _create_product(client, cat_id)
        resp = await client.delete(f"{BASE}/{created['id']}")
        assert resp.status_code == 204

    async def test_deleted_product_returns_404_on_get(
        self, client: AsyncClient
    ) -> None:
        cat_id = await _create_category(client, "Gone")
        created = await _create_product(client, cat_id, "Gone Product", "GONE-001")
        await client.delete(f"{BASE}/{created['id']}")
        resp = await client.get(f"{BASE}/{created['id']}")
        assert resp.status_code == 404

    async def test_delete_unknown_returns_404(self, client: AsyncClient) -> None:
        resp = await client.delete(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404
