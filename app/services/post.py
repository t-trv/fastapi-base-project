from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import NotFoundError
from app.models.post import Post
from app.repositories.post import post_repository
from app.repositories.user import user_repository
from app.schemas.post import PostCreate, PostUpdate


async def get_post_by_id(db: AsyncSession, post_id: int) -> Post:
    post = await post_repository.get(
        db, post_id, options=[joinedload(Post.user)]
    )
    if not post:
        raise NotFoundError(detail="Post not found")
    return post


async def get_posts_list(
    db: AsyncSession,
    **kwargs,
) -> tuple[list[Post], int, int, int]:
    return await post_repository.get_list(
        db,
        search_columns=["title", "content"],
        options=[joinedload(Post.user)],
        **kwargs,
    )


async def create_post(db: AsyncSession, post_in: PostCreate) -> Post:
    # Kiểm tra user_id có tồn tại không
    user = await user_repository.get(db, post_in.user_id)
    if not user:
        raise NotFoundError(detail="User not found")

    post_data = post_in.model_dump()
    post = await post_repository.create(db, post_data)
    # Load lại relationship user cho response
    return await get_post_by_id(db, post.id)


async def create_posts_bulk(
    db: AsyncSession, posts_in: list[PostCreate]
) -> list[Post]:
    if not posts_in:
        return []

    # 1. Kiểm tra tất cả user_ids có tồn tại không
    user_ids = list({p.user_id for p in posts_in})
    users = await user_repository.get_by_ids(db, user_ids)
    user_map = {u.id: u for u in users}

    missing_user_ids = set(user_ids) - set(user_map.keys())
    if missing_user_ids:
        raise NotFoundError(
            detail=f"User IDs not found: {list(missing_user_ids)}"
        )

    # 2. Tạo hàng loạt trong repo
    posts_data = [p.model_dump(exclude_unset=True) for p in posts_in]
    created_posts = await post_repository.create_bulk(db, posts_data)

    # 3. Gán quan hệ user cho từng post để trả về response
    for post in created_posts:
        post.user = user_map.get(post.user_id)

    return created_posts


async def update_post(
    db: AsyncSession, post_id: int, post_in: PostUpdate
) -> Post:
    post = await get_post_by_id(db, post_id)
    update_data = post_in.model_dump(exclude_unset=True)
    if update_data:
        post = await post_repository.update(db, post, update_data)
    return post


async def delete_post(db: AsyncSession, post_id: int) -> Post:
    post = await get_post_by_id(db, post_id)
    return await post_repository.delete(db, post)


async def delete_posts_bulk(
    db: AsyncSession, ids: list[int]
) -> list[Post]:
    if not ids:
        return []

    # 1. Lấy các objects theo danh sách ids (kèm relationship user)
    posts = await post_repository.get_by_ids(
        db, ids, options=[joinedload(Post.user)]
    )
    if not posts:
        raise NotFoundError(detail="No posts found to delete")

    # 2. Gọi delete_bulk xóa danh sách các objects này
    return await post_repository.delete_bulk(db, posts)
