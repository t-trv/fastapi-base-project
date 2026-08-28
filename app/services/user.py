from sqlalchemy.ext.asyncio import AsyncSession
from app.exceptions import NotFoundError, BadRequestError
from app.models.user import User
from app.repositories.user import user_repository
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import hash_password


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    user = await user_repository.get(db, user_id)
    if not user:
        raise NotFoundError(detail="User not found")
    return user

async def get_users_list(
    db: AsyncSession,
    **kwargs,
) -> tuple[list[User], int, int, int]:
    return await user_repository.get_list(
        db,
        search_columns=["username"],
        **kwargs,
    )

async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    # Kiểm tra username đã tồn tại chưa
    existing_user = await user_repository.get_by_username(db, user_in.username)
    if existing_user:
        raise BadRequestError(detail="Username already registered")

    # Hash password và lưu
    user_data = user_in.model_dump(exclude={"password"})
    user_data["hashed_password"] = hash_password(user_in.password)
    return await user_repository.create(db, user_data)

async def update_user(
    db: AsyncSession, user_id: int, user_in: UserUpdate
) -> User:
    user = await get_user_by_id(db, user_id)

    update_data = {}
    if user_in.username is not None:
        if user_in.username != user.username:
            existing = await user_repository.get_by_username(db, user_in.username)
            if existing:
                raise BadRequestError(detail="Username already registered")
        update_data["username"] = user_in.username

    if user_in.password is not None:
        update_data["hashed_password"] = hash_password(user_in.password)

    return await user_repository.update(db, user, update_data)

async def delete_user(db: AsyncSession, user_id: int) -> User:
    user = await get_user_by_id(db, user_id)
    return await user_repository.delete(db, user)
