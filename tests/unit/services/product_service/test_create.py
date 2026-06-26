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
    InvalidImageUrl,
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
    async def test_create_returns_product_read(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        product_id = uuid.uuid4()
        session.scalar.return_value = None

        async def _set_id(obj) -> None:
            obj.id = product_id

        session.refresh.side_effect = _set_id
        service = ProductService(session, media_settings)

        result = await service.create(_write())

        assert isinstance(result, ProductRead)
        assert result.id == product_id
        assert result.title == "Widget"
        assert result.sku == "SKU-001"
        assert result.price == Decimal("9.99")

    async def test_create_strips_base_url_before_storing(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        product_id = uuid.uuid4()
        session.scalar.return_value = None

        async def _set_id(obj) -> None:
            obj.id = product_id

        session.refresh.side_effect = _set_id
        service = ProductService(session, media_settings)

        base = media_settings.media_base_url
        data = ProductWrite(
            title="Widget",
            description=None,
            sku="SKU-001",
            price=Decimal("9.99"),
            # client sends back the absolute url it received on upload
            image_url=f"{base}/media/products/abc.png",
            product_category_id=uuid.uuid4(),
        )
        result = await service.create(data)

        stored = session.add.call_args.args[0]
        assert stored.image_url == "/media/products/abc.png"
        assert result.image_url == f"{base}/media/products/abc.png"

    async def test_create_raises_invalid_image_url_for_url_outside_base(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        session.scalar.return_value = None
        service = ProductService(session, media_settings)

        data = ProductWrite(
            title="Widget",
            description=None,
            sku="SKU-001",
            price=Decimal("9.99"),
            image_url="https://cdn.other.com/x.jpg",
            product_category_id=uuid.uuid4(),
        )

        with pytest.raises(InvalidImageUrl):
            await service.create(data)

    async def test_create_raises_category_not_found_when_category_missing(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductService(session, media_settings)

        with pytest.raises(ProductCategoryNotFoundForProduct):
            await service.create(_write())

    async def test_create_raises_duplicate_title_when_title_exists(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        session.scalar.return_value = MagicMock()
        service = ProductService(session, media_settings)

        with pytest.raises(DuplicateProductTitle):
            await service.create(_write())

    async def test_create_raises_duplicate_sku_when_sku_exists(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        session.scalar.side_effect = [None, MagicMock()]
        service = ProductService(session, media_settings)

        with pytest.raises(DuplicateProductSku):
            await service.create(_write())

    async def test_create_raises_duplicate_title_on_integrity_error(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        session.scalar.return_value = None
        session.commit.side_effect = IntegrityError(None, None, Exception())
        service = ProductService(session, media_settings)

        with pytest.raises(DuplicateProductTitle):
            await service.create(_write())

    async def test_create_logs_and_reraises_sqlalchemy_error(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        session.scalar.return_value = None
        session.commit.side_effect = SQLAlchemyError("boom")
        service = ProductService(session, media_settings)

        with pytest.raises(SQLAlchemyError):
            await service.create(_write())

        session.rollback.assert_awaited()
