import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.schemas.product_schema import ProductWrite
from app.services.errors import (
    DuplicateProductTitle,
    ProductCategoryNotFoundForProduct,
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
class TestProductServiceCreate:
    async def test_raises_category_not_found_when_category_missing(self) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductService(session)

        with pytest.raises(ProductCategoryNotFoundForProduct):
            await service.create(_write())

    async def test_raises_duplicate_title_on_integrity_error(self) -> None:
        session = AsyncMock()
        session.get.return_value = object()
        session.scalar.return_value = None
        session.commit.side_effect = IntegrityError(None, None, Exception())
        service = ProductService(session)

        with pytest.raises(DuplicateProductTitle):
            await service.create(_write())
