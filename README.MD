# FastAPI Base Project

Backend boilerplate chuẩn hóa theo kiến trúc phân lớp (Layered Architecture): `Endpoint -> Service -> Repository -> Model`.

---

## 1. Yêu cầu hệ thống

- Python 3.11+
- Docker & Docker Compose

---

## 2. Khởi chạy nhanh với Docker (Khuyên dùng)

### Bước 1: Chuẩn bị biến môi trường
```bash
cp .env.example .env
```
*(Chỉnh sửa thông số kết nối nếu cần. Mặc định đã cấu hình sẵn mạng nội bộ Docker).*

### Bước 2: Khởi chạy
```bash
docker compose up -d --build
```

- API Docs (Swagger): `http://localhost:5100/docs`
- pgAdmin: `http://localhost:8080` (Tài khoản: `admin@example.com` / `adminpassword`)
- MinIO Console: `http://localhost:9001` (`minioadmin` / `minioadminpassword`)

---

## 3. Khởi chạy trên máy Local (Không dùng Docker App)

### Bước 1: Khởi tạo môi trường ảo & cài đặt thư viện
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Bước 2: Bật Database & Redis
```bash
# Chỉ chạy DB, Redis, MinIO
docker compose up -d db redis minio
```

### Bước 3: Cấu hình môi trường
Tạo file `.env.local` để ghi đè kết nối máy local:
```env
APP_PORT=5100
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgrespassword
DB_NAME=app_db

REDIS_HOST=localhost
REDIS_PORT=6379
```

### Bước 4: Chạy Migration & Khởi động Server
- **Linux / macOS:**
  ```bash
  chmod +x run.sh && ./run.sh
  ```
- **Windows (PowerShell):**
  ```powershell
  .\run.ps1
  ```

---

## 4. Chạy Automated Tests

Hệ thống test dùng SQLite in-memory, mock sẵn Redis và Scheduler:

- **Linux / macOS:**
  ```bash
  ./run-test.sh
  ```
- **Windows (PowerShell):**
  ```powershell
  .\run-test.ps1
  ```
- **Pytest trực tiếp:**
  ```bash
  pytest -v
  ```

---

## 5. Cấu trúc thư mục

```text
├── app/
│   ├── api/v1/         # Endpoints (Route, commit DB, validate response)
│   ├── config/         # Settings, database session, redis client
│   ├── core/           # Logging, exception handlers toàn cục
│   ├── models/         # SQLAlchemy models (Base, User, Post)
│   ├── repositories/   # Truy vấn DB thuần túy (CRUD, flush ID)
│   ├── schemas/        # Pydantic v2 schemas
│   ├── services/       # Module functions xử lý business logic
│   └── utils/          # Cache, rate limit, helpers
├── tests/              # Fixtures và test cases (pytest + httpx)
├── docker-compose.yml  # Điều phối App, DB, Redis, MinIO, pgAdmin
├── Dockerfile          # Multi-stage build tối ưu cho production
└── entrypoint.sh       # Script tự động migrate DB và chạy Uvicorn
```
