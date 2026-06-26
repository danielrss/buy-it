import uuid
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.schemas.product_category_schema import (
    ProductCategoryRead,
    ProductCategoryWrite,
)
from app.services.errors import (
    DuplicateProductCategoryName,
    ProductCategoryParentNotFound,
)
from app.services.product_category_service import ProductCategoryService


def _write(
    name: str = "Electronics", parent: uuid.UUID | None = None
) -> ProductCategoryWrite:
    return ProductCategoryWrite(name=name, parent_category_id=parent)


@pytest.mark.unit
class TestProductCategoryServiceCreate:
    async def test_create_returns_product_category_read(self) -> None:
        session = AsyncMock()
        cat_id = uuid.uuid4()

        async def _set_id(obj) -> None:
            obj.id = cat_id

        session.refresh.side_effect = _set_id
        service = ProductCategoryService(session)

        result = await service.create(_write(name="Electronics"))

        assert isinstance(result, ProductCategoryRead)
        assert result.id == cat_id
        assert result.name == "Electronics"
        assert result.parent_category_id is None

    async def test_create_raises_parent_not_found_when_parent_missing(self) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductCategoryService(session)
        parent_id = uuid.uuid4()

        with pytest.raises(ProductCategoryParentNotFound):
            await service.create(_write(parent=parent_id))

    async def test_create_raises_duplicate_name_on_integrity_error(self) -> None:
        session = AsyncMock()
        session.commit.side_effect = IntegrityError(None, None, Exception())
        service = ProductCategoryService(session)

        with pytest.raises(DuplicateProductCategoryName):
            await service.create(_write())

    async def test_create_logs_and_reraises_sqlalchemy_error(self) -> None:
        session = AsyncMock()
        session.commit.side_effect = SQLAlchemyError("boom")
        service = ProductCategoryService(session)

        with pytest.raises(SQLAlchemyError):
            await service.create(_write())

        session.rollback.assert_awaited()
