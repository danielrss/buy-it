import uuid

import pytest
from httpx import AsyncClient

BASE = "/v1/product-categories"


@pytest.mark.integration
class TestCreateProductCategory:
    async def test_create_returns_201_with_id(self, client: AsyncClient) -> None:
        resp = await client.post(BASE, json={"name": "Electronics"})
        assert resp.status_code == 201
        body = resp.json()
        assert uuid.UUID(body["id"])
        assert body["name"] == "Electronics"
        assert body["parent_category_id"] is None

    async def test_create_child_with_valid_parent(self, client: AsyncClient) -> None:
        parent = (await client.post(BASE, json={"name": "Parent"})).json()
        resp = await client.post(
            BASE, json={"name": "Child", "parent_category_id": parent["id"]}
        )
        assert resp.status_code == 201
        assert resp.json()["parent_category_id"] == parent["id"]

    async def test_create_duplicate_name_returns_409(self, client: AsyncClient) -> None:
        await client.post(BASE, json={"name": "Duplicate"})
        resp = await client.post(BASE, json={"name": "Duplicate"})
        assert resp.status_code == 409

    async def test_create_with_nonexistent_parent_returns_400(
        self, client: AsyncClient
    ) -> None:
        resp = await client.post(
            BASE, json={"name": "Orphan", "parent_category_id": str(uuid.uuid4())}
        )
        assert resp.status_code == 400
