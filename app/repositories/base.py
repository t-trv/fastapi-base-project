from datetime import datetime, timezone
from typing import Generic, TypeVar, Type, Optional, Any

from sqlalchemy import select, func, or_, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    # Hàm query chỉ lấy dữ liệu, không commit

    async def get(
        self,
        db: AsyncSession,
        id: Any,
        options: list[Any] | None = None,
        allow_deleted: bool = False,
    ) -> Optional[ModelType]:
        if options:
            pk_column = self.model.__mapper__.primary_key[0]
            stmt = select(self.model).filter(pk_column == id).options(*options)
            result = await db.execute(stmt)
            obj = result.scalars().first()
        else:
            obj = await db.get(self.model, id)

        if obj and not allow_deleted:
            if getattr(obj, "is_deleted", False) is True:
                return None
            if getattr(obj, "deleted_at", None) is not None:
                return None
        return obj

    async def get_by_ids(
        self,
        db: AsyncSession,
        ids: list[Any],
        allow_deleted: bool = False,
    ) -> list[ModelType]:
        if not ids:
            return []
        pk_column = self.model.__mapper__.primary_key[0]
        stmt = select(self.model).filter(pk_column.in_(ids))

        if not allow_deleted:
            if hasattr(self.model, "is_deleted"):
                stmt = stmt.filter(self.model.is_deleted == False)
            elif hasattr(self.model, "deleted_at"):
                stmt = stmt.filter(self.model.deleted_at.is_(None))

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def get_list(
        self,
        db: AsyncSession,
        *,
        search: str | None = None,  # Chuỗi tìm kiếm
        search_columns: list[str] | None = None,  # Các cột được phép tìm kiếm
        filters: (
            dict[str, Any] | None
        ) = None,  # Lọc dưới dạng { "column": ["value1", "value2"] } hoặc đơn trị
        filters_raw: (
            list[Any] | None
        ) = None,  # Lọc dưới dạng raw, bạn tự viết điều kiện
        sort_by: str | None = "created_at",  # Cột được sắp xếp
        sort_order: str | None = "desc",  # Thứ tự sắp xếp
        offset: int = 0,  # Vị trí bắt đầu
        limit: int = 10,  # Số lượng bản ghi
        options: list[Any] | None = None,  # Truyền vào các options (ví dụ: joinedload)
        allow_deleted: bool = False,  # Cho phép lấy cả bản ghi đã xóa soft-delete
    ) -> tuple[list[ModelType], int, int, int]:
        stmt = select(self.model)

        # 0. Xử lý options
        if options:
            stmt = stmt.options(*options)

        # 1. Xử lý Soft Delete (SỬA LỖI logic so sánh của Python)
        if not allow_deleted:
            if hasattr(self.model, "is_deleted"):
                stmt = stmt.filter(self.model.is_deleted == False)
            elif hasattr(self.model, "deleted_at"):
                stmt = stmt.filter(self.model.deleted_at.is_(None))

        # 2. Xử lý search str trên các cột được chỉ định search_columns
        if search and search_columns:
            search_conditions = []
            for column_name in search_columns:
                column = getattr(self.model, column_name, None)
                if column is not None:
                    # Ép kiểu column sang String trước khi dùng ilike
                    search_conditions.append(cast(column, String).ilike(f"%{search}%"))
            if search_conditions:
                stmt = stmt.filter(or_(*search_conditions))

        # 3. Xử lý filters
        if filters:
            for key, value in filters.items():
                column = getattr(self.model, key, None)
                if column is not None:
                    # Nếu value là list thì dùng in_, ngược lại thì dùng ==
                    if isinstance(value, list):
                        stmt = stmt.filter(column.in_(value))
                    else:
                        stmt = stmt.filter(column == value)

        # 4. Xử lý filters_raw
        if filters_raw:
            for f in filters_raw:
                stmt = stmt.filter(f)

        # 5. Xử lý sort_by và sort_order
        if sort_by and hasattr(self.model, sort_by):
            column = getattr(self.model, sort_by)
            if sort_order == "asc":
                stmt = stmt.order_by(column)
            else:
                stmt = stmt.order_by(column.desc())
        else:
            # Sort mặc định nếu sort_by không hợp lệ
            if hasattr(self.model, "created_at"):
                stmt = stmt.order_by(self.model.created_at.desc())
            else:
                pk_column = self.model.__mapper__.primary_key[0]
                stmt = stmt.order_by(pk_column.desc())

        # 6. Đếm tổng số bản ghi bất đồng bộ (Count)
        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_result = await db.execute(count_stmt)
        total = count_result.scalar_one()

        # 7. Xử lý offset & limit
        stmt = stmt.offset(offset).limit(limit)
        items_result = await db.execute(stmt)
        items = list(items_result.scalars().unique().all())

        return items, total, offset, limit

    # Tất cả các hàm mutate đều không commit trước, chỉ flush để lấy ID (db.flush())
    # Commit sẽ được thực hiện ở tầng service

    async def create(self, db: AsyncSession, dt: dict[str, Any]) -> ModelType:
        db_obj = self.model(**dt)
        db.add(db_obj)
        await db.flush()
        return db_obj

    async def update(
        self, db: AsyncSession, db_obj: ModelType, dt: dict[str, Any]
    ) -> ModelType:
        # Lấy tên khóa chính thực tế của model để thêm vào protected_fields
        pk_name = self.model.__mapper__.primary_key[0].name
        protected_fields = [pk_name, "id", "created_at", "updated_at"]

        # 1. Kiểm tra dt là dict hay Pydantic model
        if isinstance(dt, dict):
            data = dt
        else:
            data = dt.model_dump(exclude_unset=True)

        # 2. Update các field được phép update
        for field in data:
            if field not in protected_fields and hasattr(db_obj, field):
                setattr(db_obj, field, data[field])

        db.add(db_obj)
        await db.flush()
        return db_obj

    async def delete(self, db: AsyncSession, db_obj: ModelType) -> ModelType:
        if db_obj:
            has_soft_delete = False
            # 1. Cập nhật field is_deleted
            if hasattr(db_obj, "is_deleted"):
                setattr(db_obj, "is_deleted", True)
                has_soft_delete = True
            # 2. Cập nhật field deleted_at (dùng UTC)
            if hasattr(db_obj, "deleted_at"):
                setattr(db_obj, "deleted_at", datetime.now(timezone.utc))
                has_soft_delete = True

            # 3. Nếu không có field nào thì mới xóa vĩnh viễn
            if not has_soft_delete:
                await db.delete(db_obj)
            else:
                db.add(db_obj)

            await db.flush()
        return db_obj
