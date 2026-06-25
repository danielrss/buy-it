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
class TestGetProduct:
    async def test_get_returns_200(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client)
        created = await _create_product(client, cat_id)
        resp = await client.get(f"{BASE}/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["id"] == created["id"]

    async def test_get_unknown_returns_404(self, client: AsyncClient) -> None:
        resp = await client.get(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404

    async def test_list_contains_created_products(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client, "Gadgets")
        await _create_product(client, cat_id, "Alpha Product", "SKU-AAA")
        await _create_product(client, cat_id, "Beta Product", "SKU-BBB")
        resp = await client.get(BASE)
        assert resp.status_code == 200
        titles = {p["title"] for p in resp.json()}
        assert {"Alpha Product", "Beta Product"}.issubset(titles)

    async def test_list_is_ordered_by_title(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client, "Ordered")
        await _create_product(client, cat_id, "Zebra", "ZEB-001")
        await _create_product(client, cat_id, "Aardvark", "AAR-001")
        resp = await client.get(BASE)
        assert resp.status_code == 200
        titles = [p["title"] for p in resp.json()]
        aardvark_idx = titles.index("Aardvark")
        zebra_idx = titles.index("Zebra")
        assert aardvark_idx < zebra_idx
