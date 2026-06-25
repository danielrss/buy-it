import uuid

import pytest
from httpx import AsyncClient

BASE = "/v1/product-categories"


@pytest.mark.integration
class TestUpdateProductCategory:
    async def test_put_replaces_name(self, client: AsyncClient) -> None:
        created = (
            await client.post(
                BASE, json={"name": "OldName", "parent_category_id": None}
            )
        ).json()
        resp = await client.put(
            f"{BASE}/{created['id']}",
            json={"name": "NewName", "parent_category_id": None},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "NewName"
        assert resp.json()["parent_category_id"] is None

    async def test_put_unknown_returns_404(self, client: AsyncClient) -> None:
        resp = await client.put(
            f"{BASE}/{uuid.uuid4()}", json={"name": "X", "parent_category_id": None}
        )
        assert resp.status_code == 404

    async def test_put_duplicate_name_returns_409(self, client: AsyncClient) -> None:
        await client.post(BASE, json={"name": "Taken", "parent_category_id": None})
        other = (
            await client.post(BASE, json={"name": "Other", "parent_category_id": None})
        ).json()
        resp = await client.put(
            f"{BASE}/{other['id']}", json={"name": "Taken", "parent_category_id": None}
        )
        assert resp.status_code == 409
