import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.schemas.product_category_schema import ProductCategoryRead
from app.services.product_category_service import ProductCategoryService


@pytest.mark.unit
class TestProductCategoryServiceList:
    async def test_list_returns_list_of_product_category_reads(self) -> None:
        session = AsyncMock()
        cat_id = uuid.uuid4()
        mock_category = MagicMock()
        mock_category.id = cat_id
        mock_category.name = "Electronics"
        mock_category.parent_category_id = None
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_category]
        session.execute.return_value = mock_result
        service = ProductCategoryService(session)

        result = await service.list()

        assert len(result) == 1
        assert isinstance(result[0], ProductCategoryRead)
        assert result[0].id == cat_id
        assert result[0].name == "Electronics"
        assert result[0].parent_category_id is None

    async def test_list_returns_empty_list(self) -> None:
        session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        session.execute.return_value = mock_result
        service = ProductCategoryService(session)

        result = await service.list()

        assert len(result) == 0
