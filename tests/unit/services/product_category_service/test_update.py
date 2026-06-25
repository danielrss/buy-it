import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.product_category_schema import ProductCategoryWrite
from app.services.errors import ProductCategoryNotFound, ProductCategoryParentNotFound
from app.services.product_category_service import ProductCategoryService


def _write(
    name: str = "Electronics", parent: uuid.UUID | None = None
) -> ProductCategoryWrite:
    return ProductCategoryWrite(name=name, parent_category_id=parent)


@pytest.mark.unit
class TestProductCategoryServiceUpdate:
    async def test_raises_parent_not_found_on_self_reference(self) -> None:
        session = AsyncMock()
        cat_id = uuid.uuid4()
        mock_category = MagicMock()
        session.get.return_value = mock_category
        service = ProductCategoryService(session)

        with pytest.raises(ProductCategoryParentNotFound):
            await service.update(cat_id, _write(parent=cat_id))

    async def test_raises_not_found_when_category_missing(self) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductCategoryService(session)

        with pytest.raises(ProductCategoryNotFound):
            await service.update(uuid.uuid4(), _write())
