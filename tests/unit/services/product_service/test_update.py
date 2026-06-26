import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.schemas.product_schema import ProductWrite
from app.services.errors import (
    DuplicateProductSku,
    DuplicateProductTitle,
    ProductCategoryNotFoundForProduct,
    ProductNotFound,
)
from app.services.product_service import ProductService


def _write(
    title: str = "Widget",
    sku: str = "SKU-001",
    price: Decimal = Decimal("9.99"),
    category_id: uuid.UUID | None = None,
) -> ProductWrite:
    return ProductWrite(
        title=title,
        description=None,
        sku=sku,
        price=price,
        image_url=None,
        product_category_id=category_id or uuid.uuid4(),
    )


@pytest.mark.unit
class TestProductServiceUpdate:
    async def test_raises_not_found_when_product_missing(self) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductService(session)

        with pytest.raises(ProductNotFound):
            await service.update(uuid.uuid4(), _write())

    async def test_raises_duplicate_title_when_title_exists(self) -> None:
        session = AsyncMock()
        session.scalar.return_value = MagicMock()
        service = ProductService(session)

        with pytest.raises(DuplicateProductTitle):
            await service.update(uuid.uuid4(), _write())

    async def test_raises_duplicate_sku_when_sku_exists(self) -> None:
        session = AsyncMock()
        session.scalar.side_effect = [None, MagicMock()]
        service = ProductService(session)

        with pytest.raises(DuplicateProductSku):
            await service.update(uuid.uuid4(), _write())

    async def test_raises_duplicate_title_on_integrity_error(self) -> None:
        session = AsyncMock()
        session.scalar.return_value = None
        session.commit.side_effect = IntegrityError(None, None, Exception())
        service = ProductService(session)

        with pytest.raises(DuplicateProductTitle):
            await service.update(uuid.uuid4(), _write())

    async def test_raises_category_not_found_when_category_missing(self) -> None:
        session = AsyncMock()
        mock_product = MagicMock()

        async def _get_side_effect(model: type, id: uuid.UUID) -> object | None:
            from app.models.product import Product
            from app.models.product_category import ProductCategory

            if model is Product:
                return mock_product
            if model is ProductCategory:
                return None
            return None

        session.get.side_effect = _get_side_effect
        service = ProductService(session)

        with pytest.raises(ProductCategoryNotFoundForProduct):
            await service.update(uuid.uuid4(), _write())
