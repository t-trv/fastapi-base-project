import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_crud_post(client: AsyncClient):
    """Test tạo, đọc, cập nhật và xóa mềm Post."""
    # 1. Tạo user làm chủ bài viết
    user_res = await client.post(
        "/api/v1/users", json={"username": "author_post", "password": "password123"}
    )
    assert user_res.status_code == 201
    user_id = user_res.json()["id"]

    # 2. Tạo bài viết
    post_payload = {
        "title": "First Test Post",
        "content": "This is content for testing.",
        "user_id": user_id,
        "note": "A small note",
    }
    create_res = await client.post("/api/v1/posts", json=post_payload)
    assert create_res.status_code == 201
    post_data = create_res.json()
    post_id = post_data["id"]
    assert post_data["title"] == "First Test Post"
    assert post_data["id"] == post_id
    # Yêu cầu nghiệp vụ: API tạo bài viết phải trả về thông tin người tạo (owner)
    assert post_data["owner"] is not None
    assert post_data["owner"]["username"] == "author_post"


    # 3. Lấy chi tiết bài viết
    get_res = await client.get(f"/api/v1/posts/{post_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == post_id

    # 4. Cập nhật bài viết
    update_res = await client.put(
        f"/api/v1/posts/{post_id}", json={"title": "Updated Title"}
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Title"

    # 5. Xóa mềm (vào thùng rác)
    del_res = await client.delete(f"/api/v1/posts/{post_id}")
    assert del_res.status_code == 200

    # Lấy lại -> Không tìm thấy vì đã bị soft-delete
    get_after_del = await client.get(f"/api/v1/posts/{post_id}")
    assert get_after_del.status_code == 404

    # 6. Kiểm tra trong thùng rác
    trash_res = await client.get("/api/v1/posts/trash")
    assert trash_res.status_code == 200
    trashed_items = trash_res.json()["items"]
    trashed_ids = [p["id"] for p in trashed_items]
    assert post_id in trashed_ids

    # 7. Khôi phục bài viết
    restore_res = await client.post(f"/api/v1/posts/{post_id}/restore")
    assert restore_res.status_code == 200
    assert restore_res.json()["id"] == post_id

    # Lấy lại sau khi khôi phục thành công
    get_restored = await client.get(f"/api/v1/posts/{post_id}")
    assert get_restored.status_code == 200


@pytest.mark.asyncio
async def test_bulk_create_and_delete_posts(client: AsyncClient):
    """Test tính năng Bulk Create và Bulk Delete Posts."""
    # Tạo user
    user_res = await client.post(
        "/api/v1/users", json={"username": "bulk_author", "password": "password123"}
    )
    user_id = user_res.json()["id"]

    # Bulk create 3 posts
    bulk_payload = {
        "items": [
            {"title": "Bulk 1", "content": "Content 1", "user_id": user_id},
            {"title": "Bulk 2", "content": "Content 2", "user_id": user_id},
            {"title": "Bulk 3", "content": "Content 3", "user_id": user_id},
        ]
    }
    bulk_create_res = await client.post("/api/v1/posts/bulk", json=bulk_payload)
    assert bulk_create_res.status_code == 201
    created_posts = bulk_create_res.json()
    assert len(created_posts) == 3
    post_ids = [p["id"] for p in created_posts]

    # Bulk delete
    bulk_del_payload = {"ids": post_ids}
    bulk_del_res = await client.request(
        "DELETE", "/api/v1/posts/bulk", json=bulk_del_payload
    )
    assert bulk_del_res.status_code == 200
    assert len(bulk_del_res.json()) == 3


@pytest.mark.asyncio
async def test_create_post_failures(client: AsyncClient):
    """Tái hiện các trường hợp lỗi phổ biến khi tạo bài viết."""
    # 1. Lỗi: user_id không tồn tại trong hệ thống (Mong đợi 404 Not Found)
    res_not_found = await client.post(
        "/api/v1/posts",
        json={"title": "Post without user", "content": "Content", "user_id": 99999},
    )
    assert res_not_found.status_code == 404
    error_body = res_not_found.json()
    assert error_body["detail"]["message"] == "User not found"
    assert error_body["detail"]["code"] == "NOT_FOUND"

    # 2. Lỗi: Thiếu trường bắt buộc 'content' (Mong đợi 422 Unprocessable Entity)
    res_missing_field = await client.post(
        "/api/v1/posts",
        json={"title": "Missing content", "user_id": 1},
    )
    assert res_missing_field.status_code == 422

    # 3. Lỗi: 'title' là chuỗi rỗng min_length=1 (Mong đợi 422)
    res_empty_title = await client.post(
        "/api/v1/posts",
        json={"title": "", "content": "Some content", "user_id": 1},
    )
    assert res_empty_title.status_code == 422

    # 4. Lỗi: 'user_id' không hợp lệ (nhỏ hơn hoặc bằng 0 do gt=0) (Mong đợi 422)
    res_invalid_user = await client.post(
        "/api/v1/posts",
        json={"title": "Valid title", "content": "Some content", "user_id": -5},
    )
    assert res_invalid_user.status_code == 422

