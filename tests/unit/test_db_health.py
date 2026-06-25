from unittest.mock import AsyncMock

import pytest

from app.infrastructure.db.health import check_database


@pytest.mark.unit
class TestCheckDatabase:
    async def test_returns_true_when_execute_succeeds(self) -> None:
        session = AsyncMock()
        result = await check_database(session)
        assert result is True
        session.execute.assert_called_once()

    async def test_returns_false_when_execute_raises(self) -> None:
        session = AsyncMock()
        session.execute.side_effect = Exception("connection refused")
        result = await check_database(session)
        assert result is False
