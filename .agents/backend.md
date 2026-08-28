# Backend Coding Rules

## Rule 1: Kiến trúc phân tầng & Luồng xử lý (Layered Architecture)
- Luồng Request: `HTTP Request → Endpoint → Service → Repository → Database`.
- **Endpoint**: Nhận request, trả response, chuyển đổi exceptions sang HTTP status code thích hợp.
- **Service**: Xử lý logic nghiệp vụ, quản lý database transaction (`commit()` hoặc `rollback()`), raise business exceptions (`AppError`, `NotFoundError`).
- **Repository**: Chỉ thực hiện CRUD và tương tác DB trực tiếp, dùng `flush()` để lấy ID, tuyệt đối không được tự ý `commit()`. KHÔNG raise exception tại đây.

## Rule 2: Xử lý Exception & Giao dịch (Transaction)
- Service layer ném các exception như `AppError` hoặc `NotFoundError` khi có lỗi logic. Endpoint sẽ bắt các exception này và map thành các `HTTPException` tương ứng (400, 404, 422...).
- Mọi thao tác ghi DB (`create`, `update`, `delete`) trong Service phải bao quanh bởi khối `try-except` để `db.commit()` khi thành công hoặc `db.rollback()` khi có lỗi phát sinh.

## Rule 3: Type Annotation bắt buộc cho Service & Repository
- Khi khởi tạo Service kế thừa từ `BaseService`, bắt buộc khai báo rõ ràng kiểu dữ liệu của repository thuộc tính để IDE và static checker có thể phân tích:
  ```python
  class UserService(BaseService):
      def __init__(self):
          self.repository: UserRepository = UserRepository()
          super().__init__(self.repository)
  ```

## Rule 4: Pydantic Schema & BaseSchema
- Mọi schema (Pydantic models) phải kế thừa từ `BaseSchema` (chuyển đổi CamelCase tự động).
- Bắt buộc khai báo strict type hints và sử dụng `Field` để ràng buộc validation dữ liệu đầu vào.
