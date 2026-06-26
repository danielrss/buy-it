import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.product_category_schema import ProductCategoryRead
from app.services.errors import ProductCategoryNotFound
from app.services.product_category_service import ProductCategoryService


@pytest.mark.unit
class TestProductCategoryServiceGet:
    async def test_get_returns_product_category_read(self) -> None:
        session = AsyncMock()
        cat_id = uuid.uuid4()
        mock_category = MagicMock()
        mock_category.id = cat_id
        mock_category.name = "Electronics"
        mock_category.parent_category_id = None
        session.get.return_value = mock_category
        service = ProductCategoryService(session)

        result = await service.get(cat_id)

        assert isinstance(result, ProductCategoryRead)
        assert result.id == cat_id
        assert result.name == "Electronics"
        assert result.parent_category_id is None

    async def test_get_raises_not_found_when_category_missing(self) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductCategoryService(session)

        with pytest.raises(ProductCategoryNotFound):
            await service.get(uuid.uuid4())
