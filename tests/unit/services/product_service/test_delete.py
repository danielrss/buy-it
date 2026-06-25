import uuid
from unittest.mock import AsyncMock

import pytest

from app.services.errors import ProductNotFound
from app.services.product_service import ProductService


@pytest.mark.unit
class TestProductServiceDelete:
    async def test_raises_not_found_when_product_missing(self) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductService(session)

        with pytest.raises(ProductNotFound):
            await service.delete(uuid.uuid4())
