import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config import MediaSettings
from app.schemas.product_schema import ProductListQuery, ProductRead
from app.services.product_service import ProductService


@pytest.mark.unit
class TestProductServiceList:
    async def test_list_returns_list_of_product_reads(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        product_id = uuid.uuid4()
        category_id = uuid.uuid4()
        mock_product = MagicMock()
        mock_product.id = product_id
        mock_product.title = "Widget"
        mock_product.description = None
        mock_product.sku = "SKU-001"
        mock_product.price = Decimal("9.99")
        mock_product.image_url = None
        mock_product.product_category_id = category_id
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_product]
        session.execute.return_value = mock_result
        service = ProductService(session, media_settings)

        result = await service.list(ProductListQuery())

        assert len(result) == 1
        assert isinstance(result[0], ProductRead)
        assert result[0].id == product_id
        assert result[0].title == "Widget"
        assert result[0].price == Decimal("9.99")

    async def test_list_absolutizes_image_url(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        mock_product = MagicMock()
        mock_product.id = uuid.uuid4()
        mock_product.title = "Widget"
        mock_product.description = None
        mock_product.sku = "SKU-001"
        mock_product.price = Decimal("9.99")
        mock_product.image_url = "/media/products/abc.png"
        mock_product.product_category_id = uuid.uuid4()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_product]
        session.execute.return_value = mock_result
        service = ProductService(session, media_settings)

        result = await service.list(ProductListQuery())

        base = media_settings.media_base_url
        assert result[0].image_url == f"{base}/media/products/abc.png"

    async def test_list_returns_empty_list(self, media_settings: MediaSettings) -> None:
        session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        session.execute.return_value = mock_result
        service = ProductService(session, media_settings)

        result = await service.list(ProductListQuery())

        assert len(result) == 0
