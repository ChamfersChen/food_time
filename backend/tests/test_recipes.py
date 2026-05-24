import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_recipes(client: AsyncClient, auth_token):
    token, user_id = auth_token
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/recipes", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "list" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_recommend_recipes(client: AsyncClient, auth_token):
    token, user_id = auth_token
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/recipes/recommend", headers=headers)
    # May return empty if no ingredients
    assert response.status_code == 200