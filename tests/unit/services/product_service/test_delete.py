import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.errors import ProductNotFound
from app.services.product_service import ProductService


@pytest.mark.unit
class TestProductServiceDelete:
    async def test_delete_succeeds(self) -> None:
        session = AsyncMock()
        session.get.return_value = MagicMock()
        service = ProductService(session)

        await service.delete(uuid.uuid4())

        session.delete.assert_called_once()
        session.commit.assert_called_once()

    async def test_delete_raises_not_found_when_product_missing(self) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductService(session)

        with pytest.raises(ProductNotFound):
            await service.delete(uuid.uuid4())
