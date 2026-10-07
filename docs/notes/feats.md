# Roadmap & Feature Backlog (FastAPI Base Project)

> Tài liệu tổng hợp các tính năng cần phát triển để hoàn thiện FastAPI Base Project chuẩn Production.

---

## 🔐 1. Xác thực & Phân quyền (Authentication & Authorization)
- [ ] **Auth Flow cơ bản (JWT):**
  - [ ] `POST /api/v1/auth/register` (Đăng ký tài khoản)
  - [ ] `POST /api/v1/auth/login` (Đăng nhập - cấp Access & Refresh Token)
  - [ ] `POST /api/v1/auth/refresh-token` (Cấp lại Access Token mới)
  - [ ] `GET /api/v1/auth/me` (Lấy thông tin tài khoản hiện tại)
  - [ ] `POST /api/v1/auth/logout` (Đăng xuất / đưa token vào Blacklist)
- [ ] **Bảo mật mật khẩu:**
  - [ ] Hash password bằng `bcrypt` / `pwdlib` / `passlib`
- [ ] **Dependency xác thực:**
  - [ ] `get_current_user` với `OAuth2PasswordBearer`
- [ ] **Phân quyền (RBAC - Role Based Access Control):**
  - [ ] Quản lý Roles (`ADMIN`, `USER`, `MANAGER`)
  - [ ] Dependency kiểm tra quyền trên từng endpoint (vd: `@require_roles("ADMIN")`)

---

## ⚡ 2. Caching & Giới hạn truy cập (Redis & Rate Limit)
- [x] **Tích hợp Redis Async (`redis-py`):**
  - [x] Cấu hình kết nối Redis Connection Pool qua `.env`
  - [x] Caching kết quả cho `GET /api/v1/posts` và `GET /api/v1/posts/{id}` (TTL + Invalidation)
  - [x] Decorator `@cached` và `@invalidate_cache` dùng chung
  - [ ] Quản lý Blacklist JWT Token khi logout
- [x] **Rate Limiting (Chống Spam / Brute-force):**
  - [x] Decorator `@rate_limit(limit=5, window=60)` kiểm soát theo IP / Client (HTTP 429)
- [ ] **Distributed Lock (Khóa phân tán):**
  - [ ] Helper / Context Manager `redis_lock` chống Race Condition
- [ ] **Realtime Pub/Sub & Leaderboard (ZSET):**
  - [ ] Bảng xếp hạng / Bộ đếm view realtime với Redis Sorted Sets

---

## 📁 3. Quản lý File Upload & Media Storage
- [ ] **API Upload File (`POST /api/v1/upload`):**
  - [ ] Hỗ trợ upload ảnh/video/tài liệu (single & multiple files)
  - [ ] Validate MIME type (chỉ cho phép `.jpg`, `.png`, `.mp4`, `.pdf`...)
  - [ ] Giới hạn dung lượng file tối đa (vd: max 10MB)
- [ ] **Storage Provider linh hoạt:**
  - [ ] Local Storage (Lưu trong thư mục `static/media`)
  - [ ] S3 / MinIO / Cloudinary Storage Driver

---

## 🔍 4. Giám sát & Middleware (Observability & Tracing)
- [ ] **Health Check Endpoint:**
  - [ ] `GET /healthz` hoặc `GET /api/v1/health` (Kiểm tra kết nối Database, Redis, Scheduler)
- [ ] **Request Tracking Middleware:**
  - [ ] Tự động gán `X-Request-ID` cho mỗi request và ghi vào Loguru
  - [ ] Đo thời gian phản hồi `X-Process-Time` trả về Header

---

## 🧩 5. Database Mixins & Tiện ích Model
- [ ] **Audit & Soft Delete Mixin:**
  - [ ] Tạo `SoftDeleteMixin`: tự động có `is_deleted`, `deleted_at`
  - [ ] Tạo `AuditMixin`: tự động có `created_by`, `updated_by`, `created_at`, `updated_at`

---

## 🧪 6. Testing & DevOps (CI/CD)
- [x] **Automated Testing:**
  - [x] Cấu hình `pytest` + `pytest-asyncio` + `httpx.AsyncClient`
  - [x] Viết bộ test fixture cho Database in-memory / test SQLite
  - [x] Test cases mẫu cho CRUD, Auth, Bulk APIs
- [ ] **Docker & Deployment:**
  - [ ] `Dockerfile` chuẩn tối ưu (Multi-stage build)
  - [ ] `docker-compose.yml` (App + PostgreSQL + Redis + Adminer)