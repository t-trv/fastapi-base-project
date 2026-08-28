from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1
from app.config import settings
from app.core import setup_logging, register_exception_handlers
from app.schedulers.scheduler import setup_scheduler, shutdown_scheduler

# Khởi chạy cấu hình logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi chạy tác vụ scheduler nền
    setup_scheduler()
    yield
    # Tắt scheduler an toàn khi dừng server
    shutdown_scheduler()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Đăng ký Exception Handlers toàn cục
register_exception_handlers(app)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Router
app.include_router(api_v1, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"status": "Server is running"}
