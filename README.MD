# 🚀 FastAPI Advanced Base Project

Dự án Boilerplate Backend hiệu năng cao được xây dựng trên nền tảng **FastAPI**, tuân thủ nghiêm ngặt kiến trúc phân lớp (**Layered Architecture**: Controller/API -> Service -> Repository -> Model) và tích hợp sẵn các giải pháp chuẩn hóa cho dự án production thực tế.

---

## 🛠️ Công nghệ sử dụng

- **[FastAPI](https://fastapi.tiangolo.com/)**: Framework web hiện đại, hiệu năng cao, dựa trên Starlette và Pydantic v2.
- **[SQLAlchemy 2.0 (Async)](https://www.sqlalchemy.org/)**: ORM mạnh mẽ xử lý truy vấn cơ sở dữ liệu bất đồng bộ thông qua `asyncpg`.
- **[Alembic](https://alembic.sqlalchemy.org/)**: Công cụ quản lý và migration cấu trúc Database tự động.
- **[Pydantic v2](https://docs.pydantic.dev/latest/)**: Xác thực và chuẩn hóa dữ liệu đầu vào/đầu ra với tốc độ xử lý nhanh.
- **[Bcrypt](https://pypi.org/project/bcrypt/)**: Mã hóa và bảo mật mật khẩu người dùng.
- **PostgreSQL**: Hệ quản trị cơ sở dữ liệu quan hệ mạnh mẽ chạy trên môi trường Docker.

---

## 🏗️ Kiến trúc thư mục (Project Structure)

Dự án được tổ chức phẳng hóa ở tầng Controller và phân lớp rõ ràng để dễ bảo trì và mở rộng:

```text
api/
├── alembic/                # Quản lý migration Database
├── app/
│   ├── api/
│   │   └── v1/             # Flattened Controller (Ví dụ: user.py, telegram.py)
│   ├── config/             # Cấu hình Database, settings
│   ├── core/               # Lõi hệ thống (Logging, Exceptions registry)
│   ├── dependencies/       # Dependency Injection (Database, Auth...)
│   ├── exceptions/         # Định nghĩa các lớp lỗi nghiệp vụ tùy chỉnh (Business Errors)
│   ├── models/             # Định nghĩa cấu trúc bảng Database (SQLAlchemy Models)
│   ├── repositories/       # Tương tác cơ sở dữ liệu (CRUD base logic)
│   ├── schemas/            # Pydantic Schemas (Data validation & serialization)
│   ├── services/           # Tầng nghiệp vụ (Functional Business Logic)
│   ├── utils/              # Các công cụ hỗ trợ (JWT, Security, TelegramClient...)
│   └── main.py             # File khởi chạy ứng dụng chính
├── logs/                   # Thư mục lưu trữ log xoay vòng (app.log)
├── requirements.txt        # Danh sách thư viện phụ thuộc
├── run.sh                  # Script khởi chạy nhanh trên Linux/MacOS
└── docker-compose.yml      # Docker Compose khởi chạy DB, pgAdmin, MinIO
```

---

## 🔑 Các tính năng nổi bật đã tích hợp

### 1. Chuẩn hóa Exception & Dữ liệu Lỗi

- Tất cả các lỗi trong hệ thống (lỗi nghiệp vụ, lỗi crash 500, lỗi validate Pydantic 422, lỗi route không tồn tại) đều được bắt toàn cục và chuẩn hóa cấu trúc JSON phản hồi bằng Tiếng Anh thống nhất:
  ```json
  {
    "detail": {
      "code": "ERROR_CODE_STRING",
      "message": "Friendly error message description",
      "errors": [] // Danh sách lỗi chi tiết nếu là lỗi Validate nhiều trường
    }
  }
  ```

### 2. Hệ thống Log an toàn & Tự động khôi phục

- Ghi log vết lỗi (Traceback) chi tiết ra file `logs/app.log`.
- Tích hợp **Log Rotation**: Giới hạn tối đa **10MB** mỗi file và lưu trữ tối đa **5 file backup**.
- Tự động phát hiện file log bị xóa thủ công trong lúc server chạy và tự động khởi tạo lại file log sạch ngay lập tức để tránh lỗi gián đoạn log.

### 3. Tích hợp Telegram Bot Webhook

- **TelegramClient**: Tối ưu hiệu năng gửi tin nhắn và file bằng cách duy trì kết nối mạng (`requests.Session` Keep-Alive).
- **Webhook Endpoint** (`POST /api/v1/telegram/webhook`): Tiếp nhận các lệnh chat của admin:
  - `/getlog`: Tải và gửi trực tiếp file `logs/app.log` về Telegram của Admin bằng `BackgroundTasks` (không block request).
  - `/getusers`: Truy vấn nhanh danh sách người dùng trong Database local, format đẹp bằng Markdown và gửi về Telegram.
  - **Bảo mật Chat ID**: Chỉ cho phép Chat ID admin cấu hình trong `.env.local` thực thi lệnh. Nếu có Chat ID lạ cố tình gõ lệnh, hệ thống sẽ chặn và bắn cảnh báo bảo mật về Telegram của Admin.

---

## 🚀 Hướng dẫn cài đặt dưới local

### 1. Khởi tạo môi trường ảo Python

```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
# hoặc on Windows: .\venv\Scripts\activate
```

### 2. Cài đặt các thư viện

```bash
pip install -r requirements.txt
```

### 3. Khởi động PostgreSQL & pgAdmin qua Docker

```bash
docker compose up -d
```

- _Cơ sở dữ liệu PostgreSQL sẽ chạy tại cổng `5435` ở máy local._

### 4. Thiết lập biến môi trường

Tạo file `.env.local` dựa trên file `.env.example` và cấu hình Token Bot Telegram cùng Chat ID của bạn:

```env
APP_PORT=5102
DB_PORT=5435
DB_USER=your_db_user
DB_PASSWORD=your_db_password

# Telegram Configuration
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID=YOUR_TELEGRAM_CHAT_ID
```

### 5. Thực thi Database Migration

```bash
alembic upgrade head
```

### 6. Khởi chạy ứng dụng

```bash
./run.sh
```

- _Ứng dụng sẽ chạy tại địa chỉ: `http://localhost:5102`_
- _Trang tài liệu Swagger UI: `http://localhost:5102/docs`_

```

```
