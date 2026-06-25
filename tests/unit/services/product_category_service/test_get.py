import uuid
from unittest.mock import AsyncMock

import pytest

from app.services.errors import ProductCategoryNotFound
from app.services.product_category_service import ProductCategoryService


@pytest.mark.unit
class TestProductCategoryServiceGet:
    async def test_raises_not_found_when_category_missing(self) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductCategoryService(session)

        with pytest.raises(ProductCategoryNotFound):
            await service.get(uuid.uuid4())
