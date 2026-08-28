from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.utils.log import log_info

# Import các jobs nghiệp vụ riêng biệt
from app.schedulers.jobs.hello import hello_world_job

# Khởi tạo AsyncIOScheduler phù hợp với event loop của FastAPI
scheduler = AsyncIOScheduler()

def setup_scheduler():
    """
    Đăng ký các tác vụ lập lịch và bắt đầu scheduler.
    """
    # Đăng ký job chạy định kỳ mỗi 10 giây
    scheduler.add_job(hello_world_job, "interval", seconds=10)
    scheduler.start()
    log_info("scheduler", "Started successfully with all registered jobs.")

def shutdown_scheduler():
    """
    Dừng scheduler an toàn khi tắt máy chủ.
    """
    scheduler.shutdown()
    log_info("scheduler", "Shutdown successfully.")