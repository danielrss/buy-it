import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.errors import ProductCategoryHasChildren, ProductCategoryNotFound
from app.services.product_category_service import ProductCategoryService


@pytest.mark.unit
class TestProductCategoryServiceDelete:
    async def test_raises_not_found_when_category_missing(self) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductCategoryService(session)

        with pytest.raises(ProductCategoryNotFound):
            await service.delete(uuid.uuid4())

    async def test_raises_category_has_children_when_children_exist(self) -> None:
        session = AsyncMock()
        mock_category = MagicMock()
        session.get.return_value = mock_category
        session.scalar.return_value = 2
        service = ProductCategoryService(session)

        with pytest.raises(ProductCategoryHasChildren):
            await service.delete(uuid.uuid4())
