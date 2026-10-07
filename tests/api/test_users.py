import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_get_user(client: AsyncClient):
    """Test tạo user mới và đọc thông tin user vừa tạo."""
    payload = {
        "username": "testuser",
        "password": "strongpassword123",
    }
    # 1. Tạo user
    create_res = await client.post("/api/v1/users", json=payload)
    assert create_res.status_code == 201
    user_data = create_res.json()
    assert user_data["username"] == "testuser"
    assert "id" in user_data

    user_id = user_data["id"]

    # 2. Lấy chi tiết user
    get_res = await client.get(f"/api/v1/users/{user_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == user_id
    assert get_res.json()["username"] == "testuser"


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient):
    """Test danh sách users và phân trang."""
    # Tạo 2 users
    await client.post("/api/v1/users", json={"username": "user1", "password": "password123"})
    await client.post("/api/v1/users", json={"username": "user2", "password": "password123"})

    res = await client.get("/api/v1/users?offset=0&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "meta" in data
    assert data["meta"]["total"] >= 2
    usernames = [u["username"] for u in data["items"]]
    assert "user1" in usernames
    assert "user2" in usernames


@pytest.mark.asyncio
async def test_update_and_delete_user(client: AsyncClient):
    """Test cập nhật và xóa user."""
    # Tạo user
    create_res = await client.post(
        "/api/v1/users", json={"username": "user_to_delete", "password": "password123"}
    )
    user_id = create_res.json()["id"]

    # Cập nhật username
    update_res = await client.put(
        f"/api/v1/users/{user_id}", json={"username": "user_renamed"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["username"] == "user_renamed"

    # Xóa user
    del_res = await client.delete(f"/api/v1/users/{user_id}")
    assert del_res.status_code == 200

    # Lấy lại -> Mong đợi 404
    get_res = await client.get(f"/api/v1/users/{user_id}")
    assert get_res.status_code == 404
