import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.config import MediaSettings
from app.schemas.product_schema import ProductRead, ProductWrite
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
    async def test_update_returns_updated_product_read(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        product_id = uuid.uuid4()
        category_id = uuid.uuid4()
        mock_product = MagicMock()
        mock_product.id = product_id
        session.get.return_value = mock_product
        session.scalar.return_value = None
        service = ProductService(session, media_settings)

        data = _write(
            title="Updated Widget",
            sku="SKU-002",
            price=Decimal("19.99"),
            category_id=category_id,
        )
        result = await service.update(product_id, data)

        assert isinstance(result, ProductRead)
        assert result.id == product_id
        assert result.title == "Updated Widget"
        assert result.price == Decimal("19.99")

    async def test_update_raises_not_found_when_product_missing(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductService(session, media_settings)

        with pytest.raises(ProductNotFound):
            await service.update(uuid.uuid4(), _write())

    async def test_update_raises_duplicate_title_when_title_exists(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        session.scalar.return_value = MagicMock()
        service = ProductService(session, media_settings)

        with pytest.raises(DuplicateProductTitle):
            await service.update(uuid.uuid4(), _write())

    async def test_update_raises_duplicate_sku_when_sku_exists(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        session.scalar.side_effect = [None, MagicMock()]
        service = ProductService(session, media_settings)

        with pytest.raises(DuplicateProductSku):
            await service.update(uuid.uuid4(), _write())

    async def test_update_raises_duplicate_title_on_integrity_error(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        session.scalar.return_value = None
        session.commit.side_effect = IntegrityError(None, None, Exception())
        service = ProductService(session, media_settings)

        with pytest.raises(DuplicateProductTitle):
            await service.update(uuid.uuid4(), _write())

    async def test_update_logs_and_reraises_sqlalchemy_error(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        session.scalar.return_value = None
        session.commit.side_effect = SQLAlchemyError("boom")
        service = ProductService(session, media_settings)

        with pytest.raises(SQLAlchemyError):
            await service.update(uuid.uuid4(), _write())

        session.rollback.assert_awaited()

    async def test_update_raises_category_not_found_when_category_missing(
        self, media_settings: MediaSettings
    ) -> None:
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
        service = ProductService(session, media_settings)

        with pytest.raises(ProductCategoryNotFoundForProduct):
            await service.update(uuid.uuid4(), _write())
