import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test endpoint gốc /."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "Server is running"}
