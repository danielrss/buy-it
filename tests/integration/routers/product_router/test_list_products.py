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
    client: AsyncClient,
    *,
    title: str,
    sku: str,
    price: str,
    category_id: str,
    description: str | None = None,
    image_url: str | None = None,
) -> dict:
    resp = await client.post(
        BASE,
        json={
            "title": title,
            "description": description,
            "sku": sku,
            "price": price,
            "image_url": image_url,
            "product_category_id": category_id,
        },
    )
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.integration
class TestListProducts:
    async def test_returns_empty_list_with_no_products(
        self, client: AsyncClient
    ) -> None:
        resp = await client.get(BASE)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_returns_all_products_by_default(self, client: AsyncClient) -> None:
        cat = await _create_category(client)
        await _create_product(
            client, title="Alpha", sku="A-001", price="10.00", category_id=cat
        )
        await _create_product(
            client, title="Beta", sku="B-001", price="20.00", category_id=cat
        )
        resp = await client.get(BASE)
        assert resp.status_code == 200
        titles = [p["title"] for p in resp.json()]
        assert "Alpha" in titles
        assert "Beta" in titles

    async def test_default_sort_is_title_asc(self, client: AsyncClient) -> None:
        cat = await _create_category(client)
        await _create_product(
            client, title="Zulu", sku="Z-001", price="5.00", category_id=cat
        )
        await _create_product(
            client, title="Apple", sku="AP-001", price="5.00", category_id=cat
        )
        await _create_product(
            client, title="Mango", sku="MN-001", price="5.00", category_id=cat
        )
        resp = await client.get(BASE)
        titles = [p["title"] for p in resp.json()]
        assert titles == sorted(titles)

    async def test_sort_by_price_asc(self, client: AsyncClient) -> None:
        cat = await _create_category(client)
        await _create_product(
            client, title="Cheap", sku="CH-001", price="5.00", category_id=cat
        )
        await _create_product(
            client, title="Expensive", sku="EX-001", price="100.00", category_id=cat
        )
        await _create_product(
            client, title="Mid", sku="MD-001", price="50.00", category_id=cat
        )
        resp = await client.get(BASE, params={"sort_by": "price", "sort_order": "asc"})
        assert resp.status_code == 200
        prices = [float(p["price"]) for p in resp.json()]
        assert prices == sorted(prices)

    async def test_sort_by_price_desc(self, client: AsyncClient) -> None:
        cat = await _create_category(client)
        await _create_product(
            client, title="Cheap2", sku="CH2-001", price="5.00", category_id=cat
        )
        await _create_product(
            client, title="Expensive2", sku="EX2-001", price="100.00", category_id=cat
        )
        resp = await client.get(BASE, params={"sort_by": "price", "sort_order": "desc"})
        assert resp.status_code == 200
        prices = [float(p["price"]) for p in resp.json()]
        assert prices == sorted(prices, reverse=True)

    async def test_filter_by_category(self, client: AsyncClient) -> None:
        cat_a = await _create_category(client, "CatA")
        cat_b = await _create_category(client, "CatB")
        await _create_product(
            client, title="InA", sku="IA-001", price="10.00", category_id=cat_a
        )
        await _create_product(
            client, title="InB", sku="IB-001", price="10.00", category_id=cat_b
        )
        resp = await client.get(BASE, params={"product_category_id": cat_a})
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 1
        assert body[0]["title"] == "InA"

    async def test_filter_price_min(self, client: AsyncClient) -> None:
        cat = await _create_category(client)
        await _create_product(
            client, title="Cheap3", sku="CH3-001", price="5.00", category_id=cat
        )
        await _create_product(
            client, title="Expensive3", sku="EX3-001", price="100.00", category_id=cat
        )
        resp = await client.get(BASE, params={"price_min": 50})
        assert resp.status_code == 200
        body = resp.json()
        assert all(float(p["price"]) >= 50 for p in body)
        titles = [p["title"] for p in body]
        assert "Expensive3" in titles
        assert "Cheap3" not in titles

    async def test_filter_price_max(self, client: AsyncClient) -> None:
        cat = await _create_category(client)
        await _create_product(
            client, title="Cheap4", sku="CH4-001", price="5.00", category_id=cat
        )
        await _create_product(
            client, title="Expensive4", sku="EX4-001", price="100.00", category_id=cat
        )
        resp = await client.get(BASE, params={"price_max": 20})
        assert resp.status_code == 200
        body = resp.json()
        assert all(float(p["price"]) <= 20 for p in body)
        titles = [p["title"] for p in body]
        assert "Cheap4" in titles
        assert "Expensive4" not in titles

    async def test_filter_price_range(self, client: AsyncClient) -> None:
        cat = await _create_category(client)
        await _create_product(
            client, title="Low", sku="LW-001", price="10.00", category_id=cat
        )
        await _create_product(
            client, title="Mid2", sku="MD2-001", price="50.00", category_id=cat
        )
        await _create_product(
            client, title="High", sku="HG-001", price="200.00", category_id=cat
        )
        resp = await client.get(BASE, params={"price_min": 20, "price_max": 100})
        assert resp.status_code == 200
        body = resp.json()
        titles = [p["title"] for p in body]
        assert "Mid2" in titles
        assert "Low" not in titles
        assert "High" not in titles

    async def test_filter_with_image_true(self, client: AsyncClient) -> None:
        cat = await _create_category(client)
        await _create_product(
            client,
            title="WithImg",
            sku="WI-001",
            price="10.00",
            category_id=cat,
            image_url="https://example.com/img.jpg",
        )
        await _create_product(
            client, title="NoImg", sku="NI-001", price="10.00", category_id=cat
        )
        resp = await client.get(BASE, params={"with_image": "true"})
        assert resp.status_code == 200
        body = resp.json()
        assert all(p["image_url"] is not None for p in body)
        titles = [p["title"] for p in body]
        assert "WithImg" in titles
        assert "NoImg" not in titles

    async def test_filter_with_image_false(self, client: AsyncClient) -> None:
        cat = await _create_category(client)
        await _create_product(
            client,
            title="WithImg2",
            sku="WI2-001",
            price="10.00",
            category_id=cat,
            image_url="https://example.com/img2.jpg",
        )
        await _create_product(
            client, title="NoImg2", sku="NI2-001", price="10.00", category_id=cat
        )
        resp = await client.get(BASE, params={"with_image": "false"})
        assert resp.status_code == 200
        body = resp.json()
        assert all(p["image_url"] is None for p in body)
        titles = [p["title"] for p in body]
        assert "NoImg2" in titles
        assert "WithImg2" not in titles

    async def test_search_sku_substring_case_insensitive(
        self, client: AsyncClient
    ) -> None:
        cat = await _create_category(client)
        await _create_product(
            client, title="Gadget", sku="ABC-123", price="30.00", category_id=cat
        )
        await _create_product(
            client, title="Other", sku="XYZ-999", price="30.00", category_id=cat
        )
        resp = await client.get(BASE, params={"search": "abc"})
        assert resp.status_code == 200
        body = resp.json()
        titles = [p["title"] for p in body]
        assert "Gadget" in titles
        assert "Other" not in titles

    async def test_search_sku_partial_match(self, client: AsyncClient) -> None:
        cat = await _create_category(client)
        await _create_product(
            client, title="Widget", sku="WGT-2024-XL", price="15.00", category_id=cat
        )
        resp = await client.get(BASE, params={"search": "2024"})
        assert resp.status_code == 200
        body = resp.json()
        assert any(p["title"] == "Widget" for p in body)

    async def test_search_title_fuzzy_typo(self, client: AsyncClient) -> None:
        cat = await _create_category(client)
        await _create_product(
            client, title="Smartphone", sku="SMP-001", price="500.00", category_id=cat
        )
        # deliberate typo: "Smartphome" vs "Smartphone"
        resp = await client.get(BASE, params={"search": "Smartphome"})
        assert resp.status_code == 200
        body = resp.json()
        assert any(p["title"] == "Smartphone" for p in body)

    async def test_search_relevance_orders_closest_first(
        self, client: AsyncClient
    ) -> None:
        cat = await _create_category(client)
        await _create_product(
            client, title="Laptop Pro", sku="LP-001", price="1200.00", category_id=cat
        )
        await _create_product(
            client, title="Laptop", sku="LT-001", price="800.00", category_id=cat
        )
        # "Laptop" is closer to "Laptop" than "Laptop Pro"
        resp = await client.get(BASE, params={"search": "Laptop"})
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) >= 2
        assert body[0]["title"] == "Laptop"

    async def test_search_ignores_sort_by_param(self, client: AsyncClient) -> None:
        cat = await _create_category(client)
        await _create_product(
            client, title="Camera", sku="CAM-001", price="300.00", category_id=cat
        )
        # sort_by should be ignored when search is active; endpoint must not 500
        resp = await client.get(
            BASE, params={"search": "Camera", "sort_by": "price", "sort_order": "desc"}
        )
        assert resp.status_code == 200
        assert any(p["title"] == "Camera" for p in resp.json())

    async def test_search_no_match_returns_empty(self, client: AsyncClient) -> None:
        cat = await _create_category(client)
        await _create_product(
            client, title="Toaster", sku="TST-001", price="25.00", category_id=cat
        )
        resp = await client.get(BASE, params={"search": "xqzwvjk"})
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_combined_filter_category_and_price(
        self, client: AsyncClient
    ) -> None:
        cat_a = await _create_category(client, "FilterCatA")
        cat_b = await _create_category(client, "FilterCatB")
        await _create_product(
            client, title="Cheap in A", sku="CIA-001", price="10.00", category_id=cat_a
        )
        await _create_product(
            client,
            title="Expensive in A",
            sku="EIA-001",
            price="500.00",
            category_id=cat_a,
        )
        await _create_product(
            client, title="Cheap in B", sku="CIB-001", price="10.00", category_id=cat_b
        )
        resp = await client.get(
            BASE, params={"product_category_id": cat_a, "price_max": 100}
        )
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 1
        assert body[0]["title"] == "Cheap in A"
