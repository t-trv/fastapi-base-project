# Sử dụng base image Python chính thức bản slim để giảm dung lượng
FROM python:3.11-slim

# Thiết lập các biến môi trường
# PYTHONUNBUFFERED: Giúp log hiển thị ngay lập tức mà không bị nghẽn trong buffer
# PYTHONDONTWRITEBYTECODE: Không tạo các file .pyc để giữ image sạch sẽ
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

# Thiết lập thư mục làm việc
WORKDIR $APP_HOME

# Cài đặt các thư viện hệ thống cần thiết (cho PostgreSQL và các thư viện xử lý ảnh nếu cần)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Sao chép file requirements trước để tận dụng Docker cache
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn vào container
COPY . .

# Cấp quyền thực thi cho các script (nếu có script chạy trên Linux thay thế win_run.ps1)
RUN chmod +x /app/app/main.py

# Mở port 5100 (theo cấu hình của bạn trong mô tả)
EXPOSE 5100

# Lệnh khởi chạy ứng dụng
# Lưu ý: Sử dụng host 0.0.0.0 để có thể truy cập từ ngoài container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5100"]