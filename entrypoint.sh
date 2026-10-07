#!/bin/sh
set -e

# 1. Chạy migration tạo/cập nhật bảng trong DB
echo "Running database migrations..."
alembic upgrade head

# 2. Khởi chạy Uvicorn server với số worker tùy biến (mặc định 2 workers)
WORKERS=${WEB_CONCURRENCY:-2}
echo "Starting Uvicorn with ${WORKERS} worker(s)..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${APP_PORT:-5100} --workers ${WORKERS}
