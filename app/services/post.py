from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate

from app.repositories.post import post_repository
from app.repositories.user import user_repository


async def get_post_by_id(db: AsyncSession, post_id: int) -> Post:
    post = await post_repository.get_by_id(db, post_id, options=[joinedload(Post.user)])
    if not post:
        raise NotFoundError(detail="Post not found")
    return post


async def get_posts_list(
    db: AsyncSession,
    *,
    search: str | None = None,
    username: str | None = None,
    offset: int = 0,
    limit: int = 10,
    sort_by: str | None = "created_at",
    sort_order: str | None = "desc",
) -> tuple[list[Post], int, int, int]:
    return await post_repository.get_list(
        db,
        search=search,
        username=username,
        offset=offset,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        options=[joinedload(Post.user)],
    )


async def create_post(db: AsyncSession, post_in: PostCreate) -> Post:
    # Kiem tra user co ton tai hay khong
    user = await user_repository.get_by_id(db, post_in.user_id)
    if not user:
        raise NotFoundError(detail="User not found")

    # Create post
    post_data = post_in.model_dump(exclude_unset=True)
    post = await post_repository.create(db, post_data)

    # Set user relationship
    post.user = user

    # Return
    return post


async def create_posts_bulk(db: AsyncSession, posts_in: list[PostCreate]) -> list[Post]:
    # Check empty
    if not posts_in:
        return []

    # Lấy danh sách id người dùng theo data in
    user_ids = list({p.user_id for p in posts_in})

    # Lấy danh sách người dùng
    users = await user_repository.get_by_ids(db, user_ids)
    user_map = {u.id: u for u in users}

    # Kiểm tra danh sách người dùng có tồn tại hay không
    missing = set(user_ids) - set(user_map.keys())
    if missing:
        raise NotFoundError(detail=f"User IDs not found: {list(missing)}")

    # Create posts
    posts_data = [p.model_dump(exclude_unset=True) for p in posts_in]
    created = await post_repository.create_many(db, posts_data)

    # Set user relationship
    for post in created:
        post.user = user_map.get(post.user_id)

    # Return
    return created


async def update_post(db: AsyncSession, post_id: int, post_in: PostUpdate) -> Post:
    post = await get_post_by_id(db, post_id)
    update_data = post_in.model_dump(exclude_unset=True)
    if update_data:
        post = await post_repository.update(db, post, update_data)
    return post


async def delete_post(db: AsyncSession, post_id: int) -> Post:
    post = await get_post_by_id(db, post_id)
    return await post_repository.delete(db, post)


async def delete_posts_bulk(db: AsyncSession, ids: list[int]) -> list[Post]:
    if not ids:
        return []
    posts = await post_repository.get_by_ids(db, ids, options=[joinedload(Post.user)])
    if not posts:
        raise NotFoundError(detail="No posts found to delete")
    return await post_repository.delete_many(db, posts)


async def get_trashed_posts(
    db: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 10,
    sort_order: str | None = "desc",
) -> tuple[list[Post], int, int, int]:
    return await post_repository.get_trashed_list(
        db,
        offset=offset,
        limit=limit,
        sort_order=sort_order,
        options=[joinedload(Post.user)],
    )


async def restore_post(db: AsyncSession, post_id: int) -> Post:
    post = await post_repository.get_by_id(db, post_id, allow_deleted=True, options=[joinedload(Post.user)])
    if not post:
        raise NotFoundError(detail="Post not found")
    if post.deleted_at is None:
        raise NotFoundError(detail="Post is not in trash")
    return await post_repository.restore(db, post)


async def hard_delete_post(db: AsyncSession, post_id: int) -> None:
    post = await post_repository.get_by_id(db, post_id, allow_deleted=True)
    if not post:
        raise NotFoundError(detail="Post not found")
    if post.deleted_at is None:
        raise NotFoundError(detail="Post must be soft-deleted before hard delete")
    await post_repository.hard_delete(db, post)
