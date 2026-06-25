import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestHealth:
    async def test_health_returns_ok(self, client: AsyncClient) -> None:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
