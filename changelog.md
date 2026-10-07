# Changelog

## [1.3.0] - 2026-10-07

### Added
- **Automated Testing Suite:** Tích hợp bộ kiểm thử tự động với `pytest` + `pytest-asyncio` + `httpx.AsyncClient`.
- **In-memory SQLite Test Engine:** Cấu hình `aiosqlite` + `StaticPool` cho phép chạy test DB độc lập, tốc độ cao mà không phụ thuộc PostgreSQL thật.
- **Service Isolation & Mocking:** Tự động mock Redis và APScheduler trong lifespan khi chạy test.
- **Test Scripts:** Bổ sung script chạy test tiện lợi cho đa nền tảng: `run-test.sh` (Linux/macOS) và `run-test.ps1` (Windows/PowerShell).
- **Test Coverage Mẫu:** Viết bộ test cases hoàn chỉnh cho Root API, CRUD User, CRUD Post, Soft-delete & Restore, Bulk APIs và tái hiện các case lỗi validation/business.

## [1.2.2] - 2026-10-05

### Changed
- **Soft Delete API:** Sửa lỗi trả về null khi Soft delete các model có Soft delete bật
- **BaseRepository:** Bổ sung các hàm dùng chung `delete_bulk` và `delete_bulk_by_ids` (tự động nhận diện Soft/Hard Delete).

## [1.2.1] - 2026-09-29

### Added
- **API Rate Limit:** Implement API Rate Limit sử dụng Redis để giới hạn số request trong 1 khoảng thời gian

### Changed
- **Docker Compose:** Update docker-compose.yml để sử dụng tên service và container_name với dấu gạch dưới thay vì dấu gạch ngang - Chuẩn hóa toàn bộ.

## [1.1.1] - 2026-09-28

### Added
- **Bulk Create:** Hỗ trợ tạo hàng loạt bản ghi vào DB qua `POST /api/v1/posts/bulk` *(Hiệu năng: ~26ms / 100 bản ghi)*.
- **Bulk Delete:** Hỗ trợ xóa hàng loạt bản ghi theo danh sách ID qua `DELETE /api/v1/posts/bulk` *(Hiệu năng: ~21ms / 100 bản ghi)*.
- **BaseRepository:** Bổ sung các hàm dùng chung `create_bulk`, `delete_bulk` và `delete_bulk_by_ids` (tự động nhận diện Soft/Hard Delete).
- **Decorator `cached`:** Caching kết quả cho `GET /api/v1/posts` và `GET /api/v1/posts/{id}` (TTL + Invalidation)
- **Decorator `invalidate_cache`:** Invalidate cache khi có thay đổi dữ liệu

### Changed
- **Redis:** Cấu hình kết nối Redis Connection Pool qua `.env`