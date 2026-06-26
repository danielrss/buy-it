import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.schemas.product_category_schema import (
    ProductCategoryRead,
    ProductCategoryWrite,
)
from app.services.errors import (
    DuplicateProductCategoryName,
    ProductCategoryNotFound,
    ProductCategoryParentNotFound,
)
from app.services.product_category_service import ProductCategoryService


def _write(
    name: str = "Electronics", parent: uuid.UUID | None = None
) -> ProductCategoryWrite:
    return ProductCategoryWrite(name=name, parent_category_id=parent)


@pytest.mark.unit
class TestProductCategoryServiceUpdate:
    async def test_update_returns_updated_product_category_read(self) -> None:
        session = AsyncMock()
        cat_id = uuid.uuid4()
        mock_category = MagicMock()
        mock_category.id = cat_id
        session.get.return_value = mock_category
        service = ProductCategoryService(session)

        result = await service.update(cat_id, _write(name="Updated"))

        assert isinstance(result, ProductCategoryRead)
        assert result.id == cat_id
        assert result.name == "Updated"
        assert result.parent_category_id is None

    async def test_update_raises_parent_not_found_on_self_reference(self) -> None:
        session = AsyncMock()
        cat_id = uuid.uuid4()
        mock_category = MagicMock()
        session.get.return_value = mock_category
        service = ProductCategoryService(session)

        with pytest.raises(ProductCategoryParentNotFound):
            await service.update(cat_id, _write(parent=cat_id))

    async def test_update_raises_not_found_when_category_missing(self) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductCategoryService(session)

        with pytest.raises(ProductCategoryNotFound):
            await service.update(uuid.uuid4(), _write())

    async def test_update_raises_parent_not_found_when_parent_missing(self) -> None:
        session = AsyncMock()
        mock_category = MagicMock()
        session.get.side_effect = [mock_category, None]
        service = ProductCategoryService(session)

        with pytest.raises(ProductCategoryParentNotFound):
            await service.update(uuid.uuid4(), _write(parent=uuid.uuid4()))

    async def test_update_raises_duplicate_name_on_integrity_error(self) -> None:
        session = AsyncMock()
        session.commit.side_effect = IntegrityError(None, None, Exception())
        service = ProductCategoryService(session)

        with pytest.raises(DuplicateProductCategoryName):
            await service.update(uuid.uuid4(), _write())
