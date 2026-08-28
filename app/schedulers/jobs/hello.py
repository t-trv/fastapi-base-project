from app.utils.log import log_info

def hello_world_job():
    """
    Tác vụ in chuỗi "hello world" ra terminal định kỳ.
    """
    log_info("scheduler", "hello world")
