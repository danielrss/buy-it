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


@pytest.mark.integration
class TestCreateProduct:
    async def test_create_returns_201_with_fields(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client)
        resp = await client.post(
            BASE,
            json={
                "title": "Laptop",
                "description": None,
                "sku": "LAP-001",
                "price": "999.99",
                "image_url": None,
                "product_category_id": cat_id,
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert uuid.UUID(body["id"])
        assert body["title"] == "Laptop"
        assert body["sku"] == "LAP-001"
        assert float(body["price"]) == 999.99
        assert body["description"] is None
        assert body["image_url"] is None
        assert body["product_category_id"] == cat_id

    async def test_create_with_all_optional_fields(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client, "Gadgets")
        image_url = "http://localhost:8000/media/products/phone.jpg"
        resp = await client.post(
            BASE,
            json={
                "title": "Phone",
                "description": "A smartphone",
                "sku": "PHN-001",
                "price": "499.00",
                "image_url": image_url,
                "product_category_id": cat_id,
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["description"] == "A smartphone"
        assert body["image_url"] == image_url

    async def test_create_with_foreign_image_url_returns_422(
        self, client: AsyncClient
    ) -> None:
        cat_id = await _create_category(client, "Foreign")
        resp = await client.post(
            BASE,
            json={
                "title": "Imported",
                "description": None,
                "sku": "IMP-001",
                "price": "10.00",
                "image_url": "https://example.com/phone.jpg",
                "product_category_id": cat_id,
            },
        )
        assert resp.status_code == 422
        assert resp.json()["detail"] == "invalid image url"

    async def test_create_duplicate_title_returns_409(
        self, client: AsyncClient
    ) -> None:
        cat_id = await _create_category(client, "Home")
        payload = {
            "title": "Blender",
            "description": None,
            "sku": "BLD-001",
            "price": "49.99",
            "image_url": None,
            "product_category_id": cat_id,
        }
        await client.post(BASE, json=payload)
        payload2 = {
            "title": "Blender",
            "description": None,
            "sku": "BLD-002",
            "price": "49.99",
            "image_url": None,
            "product_category_id": cat_id,
        }
        resp = await client.post(BASE, json=payload2)
        assert resp.status_code == 409
        assert resp.json()["detail"] == "title already exists"

    async def test_create_duplicate_sku_returns_409(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client, "Tools")
        payload = {
            "title": "Drill",
            "description": None,
            "sku": "DRL-001",
            "price": "89.99",
            "image_url": None,
            "product_category_id": cat_id,
        }
        await client.post(BASE, json=payload)
        payload2 = {
            "title": "Drill Pro",
            "description": None,
            "sku": "DRL-001",
            "price": "129.99",
            "image_url": None,
            "product_category_id": cat_id,
        }
        resp = await client.post(BASE, json=payload2)
        assert resp.status_code == 409
        assert resp.json()["detail"] == "sku already exists"

    async def test_create_nonexistent_category_returns_400(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(
            BASE,
            json={
                "title": "Ghost",
                "description": None,
                "sku": "GHO-001",
                "price": "1.00",
                "image_url": None,
                "product_category_id": str(uuid.uuid4()),
            },
        )
        assert resp.status_code == 400

    async def test_create_zero_price_returns_422(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client, "Free")
        resp = await client.post(
            BASE,
            json={
                "title": "Free Thing",
                "description": None,
                "sku": "FRE-001",
                "price": "0",
                "image_url": None,
                "product_category_id": cat_id,
            },
        )
        assert resp.status_code == 422

    async def test_create_negative_price_returns_422(self, client: AsyncClient) -> None:
        cat_id = await _create_category(client, "Negative")
        resp = await client.post(
            BASE,
            json={
                "title": "Negative Price",
                "description": None,
                "sku": "NEG-001",
                "price": "-5.00",
                "image_url": None,
                "product_category_id": cat_id,
            },
        )
        assert resp.status_code == 422
