import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.config import MediaSettings
from app.services.errors import ProductNotFound
from app.services.product_service import ProductService


@pytest.mark.unit
class TestProductServiceDelete:
    async def test_delete_succeeds(self, media_settings: MediaSettings) -> None:
        session = AsyncMock()
        session.get.return_value = MagicMock()
        service = ProductService(session, media_settings)

        await service.delete(uuid.uuid4())

        session.delete.assert_called_once()
        session.commit.assert_called_once()

    async def test_delete_raises_not_found_when_product_missing(
        self, media_settings: MediaSettings
    ) -> None:
        session = AsyncMock()
        session.get.return_value = None
        service = ProductService(session, media_settings)

        with pytest.raises(ProductNotFound):
            await service.delete(uuid.uuid4())
