from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post
from app.models.user import User

from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    def __init__(self):
        super().__init__(Post)

    async def get_list(
        self,
        db: AsyncSession,
        *,
        search: str | None = None,
        username: str | None = None,
        offset: int = 0,
        limit: int = 10,
        sort_by: str | None = "created_at",
        sort_order: str | None = "desc",
        allow_deleted: bool = False,
        options: list | None = None,
    ) -> tuple[list[Post], int, int, int]:
        """Search theo title/content, filter theo username. Không generic filters dict."""

        stmt = select(self.model)
        if not allow_deleted:
            stmt = self._soft_delete_filter(stmt)
        if search:
            like = f"%{search}%"
            stmt = stmt.where(or_(self.model.title.ilike(like), self.model.content.ilike(like)))
        if username is not None:
            stmt = stmt.where(self.model.user.has(User.username == username))
        if options:
            stmt = stmt.options(*options)
        stmt = self._apply_sort(stmt, sort_by, sort_order)
        total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list((await db.execute(stmt.offset(offset).limit(limit))).scalars().unique().all())
        return items, total, offset, limit


post_repository = PostRepository()
