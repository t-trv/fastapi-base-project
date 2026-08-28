# Camera Vision API - Architecture Overview

## 1. Layered Architecture

### Request Flow

```
HTTP Request → Endpoint → Service → Repository → Database
```

### Responsibilities

| Layer          | Responsibility                                                                        |
| -------------- | ------------------------------------------------------------------------------------- |
| **Endpoint**   | Nhận HTTP request, trả HTTP response, map exception → HTTP status                     |
| **Service**    | Xử lý business logic, quản lý transaction (commit/rollback), raise business exception |
| **Repository** | CRUD operations, tương tác trực tiếp với database. KHÔNG raise exception, KHÔNG commit |

---

## 2. Exception Handling

```
Service Layer                    API Layer
AppError ────────────────────► HTTPException(400)
NotFoundError ───────────────► HTTPException(404)
ValidationError ─────────────► HTTPException(422)
```

- Service layer: raise `AppError`, `NotFoundError` (business exceptions)
- API layer: map business exceptions → `HTTPException`
- Repository: KHÔNG raise exception, KHÔNG commit

---

## 3. Transaction Management

```
Service.create() / update() / delete()
├── try:
│   ├── repo.operation()  # flush only, không commit
│   └── db.commit()
└── except:
    └── db.rollback()
```

- Repository: `flush()` để lấy ID, KHÔNG `commit()`
- Service: `commit()` toàn bộ hoặc `rollback()` nếu lỗi

---

## 4. Base Classes

### BaseRepository

| Method                            | Mô tả                                              |
| --------------------------------- | -------------------------------------------------- |
| `get(db, id, options?)`           | Lấy 1 bản ghi theo ID, hỗ trợ truyền joinedload   |
| `get_list(db, ...)`               | Lấy danh sách với search, filter, sort, phân trang |
| `create(db, data)`                | Tạo mới (flush, không commit)                      |
| `update(db, obj, data)`           | Cập nhật (flush, không commit)                     |
| `delete(db, id)`                  | Xóa (soft delete hoặc hard delete)                 |

> **Convention `joinedload`:** Eager loading options (joinedload, selectinload) được truyền từ **Service** xuống Repository qua tham số `options`. Repository không tự quyết định load strategy. Ví dụ:
> ```python
> await self.record_repo.get_list(db, options=[
>     joinedload(Record.camera).joinedload(Camera.worker),
>     joinedload(Record.camera).joinedload(Camera.space),
> ])
> ```

### BaseService

| Method                 | Mô tả                                                |
| ---------------------- | ---------------------------------------------------- |
| `get(db, id)`          | Lấy 1 bản ghi, raise NotFoundError nếu không tồn tại |
| `get_list(db, ...)`    | Lấy danh sách                                        |
| `create(db, data)`     | Tạo mới, quản lý transaction                         |
| `update(db, id, data)` | Cập nhật, quản lý transaction                        |
| `delete(db, id)`       | Xóa, quản lý transaction                             |

---

## 5. Type Annotation

```python
class UserService(BaseService):
    def __init__(self):
        self.repository: UserRepository = UserRepository()  # IDE highlight
        super().__init__(self.repository)
```

Cần explicit annotation vì IDE không tự infer type từ `super().__init__()`.

---

## 6. File Structure (thực tế)

```
app/
├── exceptions/
│   ├── __init__.py         # Export AppError, NotFoundError, BadRequestError...
│   └── http.py             # HTTPException mappings
├── repositories/
│   ├── base.py             # BaseRepository (get, get_list, create, update, delete)
│   ├── camera.py
│   ├── record.py
│   └── ...
├── services/
│   ├── base.py             # BaseService
│   ├── camera.py
│   ├── record.py
│   ├── detected_object.py
│   └── ...
├── schemas/
│   ├── base.py             # BaseSchema (camelCase conversion)
│   ├── camera.py
│   ├── record.py
│   └── ...
├── api/v1/
│   ├── __init__.py         # Router aggregation
│   ├── camera.py
│   ├── record.py
│   └── ...
└── models/
    ├── base.py
    ├── camera.py
    ├── record.py
    └── ...
```

---

## 7. Dependency Flow

```
Endpoint → Service → Repository
              ↑
         BaseService
              ↑
         BaseRepository
              ↑
           Database
```

---

## 8. TODO — Refactor trung hạn

> Các mục dưới đây **chưa được implement**, ghi lại để refactor sau.

### 8.1 Cho Service kế thừa BaseService thực sự

Hiện tại `RecordService`, `DetectedObjectService` kế thừa `BaseService` về tên nhưng tự viết lại toàn bộ CRUD và transaction logic — gây duplicate code. Cần:
- Override đúng method của BaseService thay vì viết lại từ đầu.
- Đưa transaction `try/except commit/rollback` vào BaseService, các service con chỉ override phần business logic.

### 8.2 Tách `joinedload` options ra khỏi tham số Repository

Hiện tại Service truyền `options=[joinedload(...)]` trực tiếp xuống `get_list()` của Repository. Đây là leak của ORM strategy vào layer dưới. Cần xem xét:
- Tạo method `get_with_relations()` riêng ở Service để tập trung khai báo eager loading.
- Hoặc dùng `lazy="selectin"` trên relationship model để tự động load — phù hợp khi luôn cần load relation.

### 8.3 Repository không nên raise exception

Một số nhánh trong `base.py` đang raise `BadRequestError` — vi phạm rule "Repository KHÔNG raise exception". Cần chuyển về Service layer xử lý.
