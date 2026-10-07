# ==========================================
# 1. Builder Stage: Biên dịch & build wheels
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Cài đặt công cụ biên dịch tạm thời cho các thư viện C
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Build wheels riêng vào thư mục /app/wheels để tái sử dụng
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt


# ==========================================
# 2. Final Stage: Runtime siêu nhẹ & bảo mật
# ==========================================
FROM python:3.11-slim AS runner

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_HOME=/app

WORKDIR $APP_HOME

# Chỉ cài runtime thư viện libpq cần cho PostgreSQL (bỏ toàn bộ build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt các package đã build sẵn từ builder stage
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels

# Tạo user không có quyền root (Non-root user) để tăng cường bảo mật
RUN addgroup --system appgroup && adduser --system --group appuser

# Copy mã nguồn dự án
COPY . .

# Phân quyền cho appuser và entrypoint
RUN chmod +x /app/entrypoint.sh && \
    chown -R appuser:appgroup $APP_HOME

USER appuser

EXPOSE 5100

ENTRYPOINT ["/app/entrypoint.sh"]