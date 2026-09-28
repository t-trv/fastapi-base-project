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
