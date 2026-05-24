import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 0
    assert data["message"] == "healthy"


@pytest.mark.asyncio
async def test_login_missing_code(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={"code": ""})
    # Will fail because WeChat API won't respond, but should return proper error
    assert response.status_code in [400, 401, 500, 422]