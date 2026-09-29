import functools
from typing import Callable, Optional
from fastapi import Request
from app.config.redis import get_redis
from app.exceptions import TooManyRequestsError
from app.utils.log import log_warn


def _get_client_ip(request: Optional[Request]) -> str:
    """Lấy địa chỉ IP thật của Client (hỗ trợ Nginx / Reverse Proxy)."""
    if not request:
        return "127.0.0.1"
    
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    if request.client and request.client.host:
        return request.client.host
    return "127.0.0.1"


def rate_limit(
    limit: int = 5,
    window: int = 60,
    prefix: str = "rate_limit",
    key_func: Optional[Callable[..., str]] = None,
):
    """
    Decorator giới hạn số lượng request (Rate Limiting) dùng Redis.
    
    Args:
        limit (int): Số lượng request tối đa được phép trong 1 khung thời gian.
        window (int): Khung thời gian (tính bằng giây). Mặc định 60 giây.
        prefix (str): Tiền tố cho Redis Key (vd: "posts:create", "auth:login").
        key_func (Callable): Hàm tùy biến để lấy định danh (IP, User ID, Token...).

    Usage:
        @router.post("")
        @rate_limit(limit=5, window=10, prefix="posts:create")
        async def create_post(request: Request, ...):
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            redis = await get_redis()
            if not redis:
                # Nếu Redis không khả dụng, cho phép request đi qua để không làm nghẽn hệ thống
                return await func(*args, **kwargs)

            # 1. Tìm đối tượng Request trong args/kwargs để lấy Client IP
            request_obj: Optional[Request] = None
            for arg in args:
                if isinstance(arg, Request):
                    request_obj = arg
                    break
            if not request_obj:
                for val in kwargs.values():
                    if isinstance(val, Request):
                        request_obj = val
                        break

            # 2. Xác định Identifier (Mặc định lấy Client IP)
            if key_func:
                identifier = key_func(*args, **kwargs)
            else:
                identifier = _get_client_ip(request_obj)

            # 3. Tạo Redis Key
            route_name = prefix or f"{func.__module__}:{func.__name__}"
            cache_key = f"rl:{route_name}:{identifier}"

            # 4. Tăng bộ đếm trong Redis (Atomic Increment)
            current_count = await redis.incr(cache_key)
            if current_count == 1:
                # Lần gọi đầu tiên -> Đặt thời gian sống cho Key
                await redis.expire(cache_key, window)

            # 5. Kiểm tra vượt ngưỡng
            if current_count > limit:
                ttl = await redis.ttl(cache_key)
                ttl_str = f"{ttl}s" if ttl > 0 else "a moment"
                log_warn("rate_limit", f"IP {identifier} exceeded limit ({limit}/{window}s) on {route_name}")
                raise TooManyRequestsError(
                    detail=f"Too many requests. Limit: {limit} requests per {window} seconds. Please try again in {ttl_str}."
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator
