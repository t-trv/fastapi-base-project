from fastapi import APIRouter
from .user import router as user_router
from .post import router as post_router
from .telegram import router as telegram_router

api_v1 = APIRouter()

api_v1.include_router(user_router, prefix="/users", tags=["Users"])
api_v1.include_router(post_router, prefix="/posts", tags=["Posts"])
api_v1.include_router(telegram_router, prefix="/telegram", tags=["Telegram Webhook"])
