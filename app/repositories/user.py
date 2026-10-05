from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User

from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    async def get_by_username(self, db: AsyncSession, username: str) -> User | None:
        stmt = select(self.model).where(self.model.username == username)
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_list(
        self,
        db: AsyncSession,
        *,
        search: str | None = None,
        offset: int = 0,
        limit: int = 10,
        sort_by: str | None = "created_at",
        sort_order: str | None = "desc",
        allow_deleted: bool = False,
        options: list | None = None,
    ) -> tuple[list[User], int, int, int]:
        """Override để hỗ trợ search theo username. Filter khác -> viết thêm where ở repo này."""
        if not search:
            return await super().get_list(
                db, offset=offset, limit=limit, sort_by=sort_by, sort_order=sort_order,
                allow_deleted=allow_deleted, options=options,
            )
        # có search -> build stmt riêng (tránh duplicate logic count/paginate bằng helper base)

        stmt = select(self.model).where(self.model.username.ilike(f"%{search}%"))
        if not allow_deleted:
            stmt = self._soft_delete_filter(stmt)
        if options:
            stmt = stmt.options(*options)
        stmt = self._apply_sort(stmt, sort_by, sort_order)
        total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list((await db.execute(stmt.offset(offset).limit(limit))).scalars().unique().all())
        return items, total, offset, limit


user_repository = UserRepository()
