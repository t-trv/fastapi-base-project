import os
import logging
from logging.handlers import RotatingFileHandler

class SafeRotatingFileHandler(RotatingFileHandler):
    """
    RotatingFileHandler tùy biến tự động phát hiện và tạo lại file log
    nếu file bị xóa thủ công trên đĩa cứng trong lúc server đang chạy.
    """
    def emit(self, record):
        if not os.path.exists(self.baseFilename):
            self.close()  # Đóng luồng hiện tại để buộc Python tạo lại file mới ở lệnh ghi kế tiếp
        super().emit(record)

def setup_logging():
    """
    Cấu hình hệ thống ghi log xoay vòng (Log Rotation) cho ứng dụng.

    Cơ chế hoạt động:
    - Đảm bảo thư mục 'logs/' được tạo tự động nếu chưa tồn tại.
    - Ghi log lỗi vào file 'logs/app.log'.
    - Sử dụng SafeRotatingFileHandler giới hạn kích thước tối đa mỗi file là 10 MB.
    - Khi file log đạt giới hạn, tự động xoay vòng và giữ lại tối đa 5 file backup gần nhất.
    - Thiết lập mức log là ERROR để chỉ ghi nhận các lỗi crash hệ thống, giúp tối ưu I/O đĩa cứng.
    """
    # Đảm bảo thư mục logs tồn tại và cấu hình ghi log xoay vòng (max 10MB, max 5 files)
    os.makedirs("logs", exist_ok=True)
    file_formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    file_handler = SafeRotatingFileHandler(
        "logs/app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.ERROR)

    logger = logging.getLogger("uvicorn.error")
    logger.addHandler(file_handler)
