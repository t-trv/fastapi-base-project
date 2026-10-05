from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Template gọn cho mọi model. Chỉ giữ 6 thao tác lặp lại ở 100% repo.

    Search / filter riêng của từng domain -> viết tường minh ở repo con,
    không generic hoá bằng `filters: dict[str, Any]`.
    """

    def __init__(self, model: type[ModelType]):
        self.model = model

    # -- helpers -------------------------------------------------------------
    def _soft_delete_filter(self, stmt):
        if hasattr(self.model, "is_deleted"):
            return stmt.where(self.model.is_deleted == False)  # noqa: E712
        if hasattr(self.model, "deleted_at"):
            return stmt.where(self.model.deleted_at.is_(None))
        return stmt

    def _is_soft_deleted(self, obj: ModelType) -> bool:
        if getattr(obj, "is_deleted", False) is True:
            return True
        if getattr(obj, "deleted_at", None) is not None:
            return True
        return False

    def _apply_sort(self, stmt, sort_by: str | None, sort_order: str | None):
        col = getattr(self.model, sort_by, None) if sort_by else None
        if col is not None:
            return stmt.order_by(col if sort_order == "asc" else col.desc())
        # fallback
        if hasattr(self.model, "created_at"):
            return stmt.order_by(self.model.created_at.desc())
        pk = self.model.__mapper__.primary_key[0]
        return stmt.order_by(pk.desc())

    # -- read ----------------------------------------------------------------
    async def get_by_id(
        self,
        db: AsyncSession,
        id: Any,
        *,
        options: list[Any] | None = None,
        allow_deleted: bool = False,
    ) -> ModelType | None:
        if options:
            pk = self.model.__mapper__.primary_key[0]
            stmt = select(self.model).where(pk == id).options(*options)
            obj = (await db.execute(stmt)).scalars().first()
        else:
            obj = await db.get(self.model, id)
        if obj and not allow_deleted and self._is_soft_deleted(obj):
            return None
        return obj

    async def get_by_ids(
        self,
        db: AsyncSession,
        ids: list[Any],
        *,
        options: list[Any] | None = None,
        allow_deleted: bool = False,
    ) -> list[ModelType]:
        if not ids:
            return []
        pk = self.model.__mapper__.primary_key[0]
        stmt = select(self.model).where(pk.in_(ids))
        if not allow_deleted:
            stmt = self._soft_delete_filter(stmt)
        if options:
            stmt = stmt.options(*options)
        return list((await db.execute(stmt)).scalars().unique().all())

    async def get_list(
        self,
        db: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 10,
        sort_by: str | None = "created_at",
        sort_order: str | None = "desc",
        allow_deleted: bool = False,
        options: list[Any] | None = None,
    ) -> tuple[list[ModelType], int, int, int]:
        stmt = select(self.model)
        if not allow_deleted:
            stmt = self._soft_delete_filter(stmt)
        if options:
            stmt = stmt.options(*options)
        stmt = self._apply_sort(stmt, sort_by, sort_order)

        total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = list((await db.execute(stmt.offset(offset).limit(limit))).scalars().unique().all())
        return items, total, offset, limit

    async def get_trashed_list(
        self,
        db: AsyncSession,
        *,
        offset: int = 0,
        limit: int = 10,
        sort_order: str | None = "desc",
        options: list[Any] | None = None,
    ) -> tuple[list[ModelType], int, int, int]:
        if not hasattr(self.model, "deleted_at") and not hasattr(self.model, "is_deleted"):
            return [], 0, offset, limit
        if hasattr(self.model, "deleted_at"):
            stmt = select(self.model).where(self.model.deleted_at.is_not(None)).order_by(  # type: ignore[attr-defined]
                self.model.deleted_at.desc() if sort_order != "asc" else self.model.deleted_at.asc()  # type: ignore[attr-defined]
            )
        else:
            stmt = select(self.model).where(self.model.is_deleted == True)  # type: ignore[attr-defined]  # noqa: E712
            stmt = self._apply_sort(stmt, "created_at", sort_order)
        if options:
            stmt = stmt.options(*options)
        total = (await db.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one() or 0
        items = list((await db.execute(stmt.offset(offset).limit(limit))).scalars().unique().all())
        return items, total, offset, limit

    # -- write (flush only, commit ở tầng api) -------------------------------
    async def create(self, db: AsyncSession, data: dict[str, Any]) -> ModelType:
        obj = self.model(**data)
        db.add(obj)
        await db.flush()
        return obj

    async def create_many(self, db: AsyncSession, items: list[dict[str, Any]]) -> list[ModelType]:
        if not items:
            return []
        objs = [self.model(**d) for d in items]
        db.add_all(objs)
        await db.flush()
        return objs

    async def update(self, db: AsyncSession, obj: ModelType, data: dict[str, Any]) -> ModelType:
        pk_name = self.model.__mapper__.primary_key[0].name
        protected = {pk_name, "id", "created_at", "updated_at"}
        if not isinstance(data, dict):
            data = data.model_dump(exclude_unset=True)
        for k, v in data.items():
            if k not in protected and hasattr(obj, k):
                setattr(obj, k, v)
        db.add(obj)
        await db.flush()
        return obj

    async def delete(self, db: AsyncSession, obj: ModelType) -> ModelType:
        has_soft = False
        if hasattr(obj, "is_deleted"):
            setattr(obj, "is_deleted", True)
            has_soft = True
        if hasattr(obj, "deleted_at"):
            setattr(obj, "deleted_at", datetime.now(timezone.utc))
            has_soft = True
        if not has_soft:
            await db.delete(obj)
        else:
            db.add(obj)
        await db.flush()
        return obj

    async def delete_many(self, db: AsyncSession, objs: list[ModelType]) -> list[ModelType]:
        if not objs:
            return []
        for o in objs:
            await self.delete(db, o)
        return objs

    async def restore(self, db: AsyncSession, obj: ModelType) -> ModelType:
        if hasattr(obj, "is_deleted"):
            setattr(obj, "is_deleted", False)
        if hasattr(obj, "deleted_at"):
            setattr(obj, "deleted_at", None)
        if not hasattr(obj, "is_deleted") and not hasattr(obj, "deleted_at"):
            return obj
        db.add(obj)
        await db.flush()
        return obj

    async def hard_delete(self, db: AsyncSession, obj: ModelType) -> None:
        await db.delete(obj)
        await db.flush()
