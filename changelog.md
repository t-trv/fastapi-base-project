# Changelog

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