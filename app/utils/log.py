import logging

# Sử dụng logger chuẩn của Uvicorn để output đồng bộ với hệ thống
logger = logging.getLogger("uvicorn.error")

"""
Quy định ghi log đơn giản cho hệ thống:
Mỗi dòng log xuất ra theo format: INFO/WARNING/ERROR: [MODULE] nội dung_log
Ví dụ:
    [AUTH] Tên người dùng thao tác: admin123
    [WORKER] Tiến trình update: old_cccd=031205001877, new_cccd=031205001877
    [WORKER] CCCD không đổi (031205001877). Đang kiểm tra xem subject đã có trên camera_api chưa...
    [WORKER] Đang kiểm tra subject 031205001877 trên camera_api...
    [WORKER] Subject 031205001877 ĐÃ TỒN TẠI bên camera_api.
    [WORKER] Subject 031205001877 đã có sẵn bên camera_api.
"""

def log_info(module: str, msg: str) -> None:
    """Ghi nhận log thông tin (INFO)"""
    logger.info(f"[{module.upper()}] {msg}")

def log_warn(module: str, msg: str) -> None:
    """Ghi nhận log cảnh báo (WARNING)"""
    logger.warning(f"[{module.upper()}] {msg}")

def log_error(module: str, msg: str) -> None:
    """Ghi nhận log lỗi (ERROR)"""
    logger.error(f"[{module.upper()}] {msg}")
