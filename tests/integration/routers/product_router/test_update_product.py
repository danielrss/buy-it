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
class TestUpdateProduct:
    async def test_put_replaces_fields(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client)
        created = await _create_product(client, cat_id)
        resp = await client.put(
            f"{BASE}/{created['id']}",
            json={
                "title": "Updated Laptop",
                "description": "Now with more RAM",
                "sku": "LAP-002",
                "price": "1199.00",
                "image_url": None,
                "product_category_id": cat_id,
            },
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["title"] == "Updated Laptop"
        assert body["sku"] == "LAP-002"
        assert float(body["price"]) == 1199.00
        assert body["description"] == "Now with more RAM"

    async def test_put_unknown_returns_404(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client, "Ghost")
        resp = await client.put(
            f"{BASE}/{uuid.uuid4()}",
            json={
                "title": "X",
                "description": None,
                "sku": "X-001",
                "price": "1.00",
                "image_url": None,
                "product_category_id": cat_id,
            },
        )
        assert resp.status_code == 404

    async def test_put_duplicate_title_returns_409(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client, "Dupes")
        await _create_product(client, cat_id, "Taken Title", "TAK-001")
        other = await _create_product(client, cat_id, "Other", "OTH-001")
        resp = await client.put(
            f"{BASE}/{other['id']}",
            json={
                "title": "Taken Title",
                "description": None,
                "sku": "OTH-002",
                "price": "1.00",
                "image_url": None,
                "product_category_id": cat_id,
            },
        )
        assert resp.status_code == 409
        assert resp.json()["detail"] == "title already exists"

    async def test_put_duplicate_sku_returns_409(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client, "SKUDupes")
        await _create_product(client, cat_id, "First", "TAKEN-SKU")
        other = await _create_product(client, cat_id, "Second", "SEC-001")
        resp = await client.put(
            f"{BASE}/{other['id']}",
            json={
                "title": "Second Updated",
                "description": None,
                "sku": "TAKEN-SKU",
                "price": "1.00",
                "image_url": None,
                "product_category_id": cat_id,
            },
        )
        assert resp.status_code == 409
        assert resp.json()["detail"] == "sku already exists"

    async def test_put_nonexistent_category_returns_400(
        self, client: AsyncClient
    ) -> None:
        cat_id = await _create_category(client, "Valid")
        created = await _create_product(client, cat_id)
        resp = await client.put(
            f"{BASE}/{created['id']}",
            json={
                "title": "Laptop",
                "description": None,
                "sku": "LAP-001",
                "price": "1.00",
                "image_url": None,
                "product_category_id": str(uuid.uuid4()),
            },
        )
        assert resp.status_code == 400

    async def test_put_can_keep_same_title_and_sku(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client, "SameTitle")
        created = await _create_product(client, cat_id, "SameTitle Product", "SAME-001")
        resp = await client.put(
            f"{BASE}/{created['id']}",
            json={
                "title": "SameTitle Product",
                "description": None,
                "sku": "SAME-001",
                "price": "5.00",
                "image_url": None,
                "product_category_id": cat_id,
            },
        )
        assert resp.status_code == 200
        assert float(resp.json()["price"]) == 5.00
