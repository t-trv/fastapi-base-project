# Changelog

## [1.1.1] - 2026-09-28

### Added
- **Bulk Create:** Hỗ trợ tạo hàng loạt bản ghi vào DB qua `POST /api/v1/posts/bulk` *(Hiệu năng: ~26ms / 100 bản ghi)*.
- **Bulk Delete:** Hỗ trợ xóa hàng loạt bản ghi theo danh sách ID qua `DELETE /api/v1/posts/bulk` *(Hiệu năng: ~21ms / 100 bản ghi)*.
- **BaseRepository:** Bổ sung các hàm dùng chung `create_bulk`, `delete_bulk` và `delete_bulk_by_ids` (tự động nhận diện Soft/Hard Delete).
