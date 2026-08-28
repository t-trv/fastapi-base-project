from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        stmt = select(self.model).filter(self.model.username == username)
        result = await db.execute(stmt)
        return result.scalars().first()


user_repository = UserRepository()
