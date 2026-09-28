import functools
import hashlib
import json
from typing import Any, Callable, Sequence
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request, Response
from app.config.redis import get_cache, set_cache, delete_cache_pattern


def _serialize_value(val: Any) -> Any:
    """Helper chuyển đổi Pydantic model hoặc danh sách sang JSON serializable."""
    if isinstance(val, BaseModel):
        return val.model_dump(mode="json")
    if isinstance(val, list):
        return [_serialize_value(item) for item in val]
    if isinstance(val, dict):
        return {k: _serialize_value(v) for k, v in val.items()}
    return val


def _generate_cache_key(func: Callable, prefix: str | None, args: tuple, kwargs: dict) -> str:
    """Tạo cache key duy nhất từ tên hàm và các tham số (bỏ qua db, request, response)."""
    key_prefix = prefix or f"{func.__module__}:{func.__name__}"
    
    # Lọc bỏ các tham số không dùng để tạo key như DB Session, FastAPI Request/Response
    filtered_kwargs = {}
    for k, v in kwargs.items():
        if isinstance(v, (AsyncSession, Request, Response)):
            continue
        if isinstance(v, BaseModel):
            filtered_kwargs[k] = v.model_dump(mode="json")
        else:
            filtered_kwargs[k] = v

    filtered_args = [
        arg.model_dump(mode="json") if isinstance(arg, BaseModel) else arg
        for arg in args
        if not isinstance(arg, (AsyncSession, Request, Response))
    ]

    # Băm tham số thành chuỗi md5 nếu tham số dài, hoặc dùng json thuần
    payload = {"args": filtered_args, "kwargs": filtered_kwargs}
    raw_str = json.dumps(payload, sort_keys=True, default=str)
    
    if len(raw_str) > 100:
        param_hash = hashlib.md5(raw_str.encode()).hexdigest()
        return f"{key_prefix}:{param_hash}"
    return f"{key_prefix}:{raw_str}"


def cached(expire: int = 60, prefix: str | None = None):
    """
    Decorator tự động Cache kết quả của hàm Async vào Redis.
    
    Usage:
        @cached(expire=60, prefix="posts:list")
        async def list_posts(...):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = _generate_cache_key(func, prefix, args, kwargs)
            
            # 1. Kiểm tra cache trong Redis
            cached_val = await get_cache(cache_key)
            if cached_val is not None:
                return cached_val

            # 2. Nếu chưa có -> Thực thi hàm
            result = await func(*args, **kwargs)

            # 3. Lưu kết quả vào Redis
            if result is not None:
                serialized = _serialize_value(result)
                await set_cache(cache_key, serialized, expire=expire)

            return result
        return wrapper
    return decorator


def invalidate_cache(patterns: Sequence[str]):
    """
    Decorator tự động xóa các cache key khớp với pattern sau khi hàm chạy xong.
    
    Usage:
        @invalidate_cache(patterns=["posts:list:*", "posts:detail:*"])
        async def create_post(...):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            for pattern in patterns:
                await delete_cache_pattern(pattern)
            return result
        return wrapper
    return decorator
