import asyncio
import inspect
from app.utils.log import log_warn, log_error, log_info

# Lưu giữ reference của các background task để tránh bị Garbage Collector thu hồi giữa chừng (lỗi phổ biến ở Python 3.7+)
_background_tasks = set()


def run_in_background(func_or_coro, *args, **kwargs):
    """
    Tiện ích chạy một function (sync hoặc async) ngầm ở background (fire and forget) 
    mà không làm block luồng hiện tại.
    Có thể dùng ở mọi nơi trong app miễn là đang có event loop hoạt động.
    
    Cách sử dụng:
        from app.utils import run_in_background
        
        # Với hàm async:
        run_in_background(my_async_func(data))
        
        # Với hàm sync (sẽ được đẩy vào threadpool để không block event loop):
        run_in_background(my_sync_func, arg1, kwarg2="val")
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        log_warn("BACKGROUND_TASK", "Không tìm thấy Event Loop đang chạy, không thể khởi tạo background task.")
        return None

    if asyncio.iscoroutine(func_or_coro):
        # Nếu truyền vào coroutine (đã gọi hàm): run_in_background(my_async_func())
        task = loop.create_task(func_or_coro)
    elif inspect.iscoroutinefunction(func_or_coro):
        # Nếu truyền function pointer async: run_in_background(my_async_func, args...)
        task = loop.create_task(func_or_coro(*args, **kwargs))
    else:
        # Nếu truyền function sync: đẩy vào threadpool
        import functools
        bound_func = functools.partial(func_or_coro, *args, **kwargs)
        task = loop.create_task(asyncio.to_thread(bound_func))
    
    # Thêm vào set để giữ tham chiếu (reference)
    _background_tasks.add(task)
    
    # Hàm callback xử lý dọn dẹp và log lỗi khi task chạy xong (hoặc fail)
    task_name = getattr(func_or_coro, '__name__', 'unknown_task')
    log_info("BACKGROUND_TASK", f"Đã khởi tạo background task: {task_name}")

    def _on_task_done(t):
        _background_tasks.discard(t)
        try:
            t.result()
            log_info("BACKGROUND_TASK", f"Background task '{task_name}' đã hoàn thành thành công.")
        except asyncio.CancelledError:
            log_warn("BACKGROUND_TASK", f"Background task '{task_name}' đã bị hủy (cancelled).")
        except Exception as e:
            log_error("BACKGROUND_TASK", f"Background task '{task_name}' thất bại: {e}")

    # Đăng ký callback
    task.add_done_callback(_on_task_done)
    
    return task
