import uuid

import pytest
from httpx import AsyncClient

BASE = "/v1/product-categories"
PRODUCTS_BASE = "/v1/products"


async def _create_product(
    client: AsyncClient, category_id: str, sku: str, title: str
) -> dict:
    resp = await client.post(
        PRODUCTS_BASE,
        json={
            "title": title,
            "description": None,
            "sku": sku,
            "price": "9.99",
            "image_url": None,
            "product_category_id": category_id,
        },
    )
    return resp.json()


@pytest.mark.integration
class TestDeleteProductCategory:
    async def test_delete_child_returns_204(self, client: AsyncClient) -> None:
        parent = (
            await client.post(
                BASE, json={"name": "DelParent", "parent_category_id": None}
            )
        ).json()
        child = (
            await client.post(
                BASE, json={"name": "DelChild", "parent_category_id": parent["id"]}
            )
        ).json()
        resp = await client.delete(f"{BASE}/{child['id']}")
        assert resp.status_code == 204

    async def test_delete_parent_with_child_returns_409(
        self, client: AsyncClient
    ) -> None:
        parent = (
            await client.post(
                BASE, json={"name": "BlockedParent", "parent_category_id": None}
            )
        ).json()
        await client.post(
            BASE, json={"name": "BlockedChild", "parent_category_id": parent["id"]}
        )
        resp = await client.delete(f"{BASE}/{parent['id']}")
        assert resp.status_code == 409

    async def test_delete_parent_after_child_removed_returns_204(
        self, client: AsyncClient
    ) -> None:
        parent = (
            await client.post(
                BASE, json={"name": "FreeParent", "parent_category_id": None}
            )
        ).json()
        child = (
            await client.post(
                BASE, json={"name": "FreeChild", "parent_category_id": parent["id"]}
            )
        ).json()
        await client.delete(f"{BASE}/{child['id']}")
        resp = await client.delete(f"{BASE}/{parent['id']}")
        assert resp.status_code == 204
        assert (await client.get(f"{BASE}/{parent['id']}")).status_code == 404

    async def test_delete_category_with_product_returns_409(
        self, client: AsyncClient
    ) -> None:
        category = (
            await client.post(
                BASE, json={"name": "WithProduct", "parent_category_id": None}
            )
        ).json()
        await _create_product(client, category["id"], "DEL-SKU-1", "DelProduct1")
        resp = await client.delete(f"{BASE}/{category['id']}")
        assert resp.status_code == 409
        assert resp.json()["detail"] == "category has products"

    async def test_delete_category_after_product_removed_returns_204(
        self, client: AsyncClient
    ) -> None:
        category = (
            await client.post(
                BASE, json={"name": "FreeProductCat", "parent_category_id": None}
            )
        ).json()
        product = await _create_product(
            client, category["id"], "DEL-SKU-2", "DelProduct2"
        )
        await client.delete(f"{PRODUCTS_BASE}/{product['id']}")
        resp = await client.delete(f"{BASE}/{category['id']}")
        assert resp.status_code == 204
        assert (await client.get(f"{BASE}/{category['id']}")).status_code == 404

    async def test_delete_unknown_returns_404(self, client: AsyncClient) -> None:
        resp = await client.delete(f"{BASE}/{uuid.uuid4()}")
        assert resp.status_code == 404
