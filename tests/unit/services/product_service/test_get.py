import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.product_schema import ProductRead
from app.services.errors import ProductNotFound
from app.services.product_service import ProductService


@pytest.mark.unit
class TestProductServiceGet:
    async def test_get_returns_product_read(self) -> None:
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
        session.get.return_value = mock_product
        service = ProductService(session)

        result = await service.get(product_id)

        assert isinstance(result, ProductRead)
        assert result.id == product_id
        assert result.title == "Widget"
        assert result.price == Decimal("9.99")

    async def test_get_raises_not_found_when_product_missing(self) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductService(session)

        with pytest.raises(ProductNotFound):
            await service.get(uuid.uuid4())
