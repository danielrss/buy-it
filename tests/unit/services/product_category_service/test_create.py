import uuid
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.schemas.product_category_schema import ProductCategoryWrite
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
    async def test_raises_parent_not_found_when_parent_missing(self) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductCategoryService(session)
        parent_id = uuid.uuid4()

        with pytest.raises(ProductCategoryParentNotFound):
            await service.create(_write(parent=parent_id))

    async def test_raises_duplicate_name_on_integrity_error(self) -> None:
        session = AsyncMock()
        session.commit.side_effect = IntegrityError(None, None, Exception())
        service = ProductCategoryService(session)

        with pytest.raises(DuplicateProductCategoryName):
            await service.create(_write())
