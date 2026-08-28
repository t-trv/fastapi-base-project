import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from app.exceptions import AppError

def register_exception_handlers(app: FastAPI):
    """
    Đăng ký toàn bộ các Exception Handlers toàn cục cho ứng dụng FastAPI.

    Giúp chuẩn hóa mọi response lỗi trả về cho client theo cấu trúc JSON thống nhất:
    {
        "detail": {
            "code": "ERROR_CODE",
            "message": "Thông điệp lỗi chi tiết"
        }
    }
    """

    @app.exception_handler(AppError)
    def app_error_handler(_: Request, exc: AppError):
        """
        Xử lý các lỗi nghiệp vụ (Business Errors) được ném ra chủ động từ Service layer.
        Ví dụ: NotFoundError (404), BadRequestError (400), ConflictError (409).
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": {
                    "code": exc.error_code,
                    "message": exc.detail,
                }
            },
        )

    @app.exception_handler(Exception)
    def universal_exception_handler(_: Request, exc: Exception):
        """
        Xử lý các lỗi runtime chưa được bắt (Unhandled Errors) như ZeroDivisionError, AttributeError...
        - Tự động ghi lại vết lỗi (Traceback) chi tiết vào file log hệ thống để debug.
        - Trả về mã lỗi 500 kèm lời nhắn thân thiện bằng Tiếng Anh.
        """
        logger = logging.getLogger("uvicorn.error")
        logger.error(f"Unhandled error occurred: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An internal server error occurred. Please try again later.",
                }
            },
        )

    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(_: Request, exc: RequestValidationError):
        """
        Xử lý lỗi validate dữ liệu đầu vào khi Client gửi sai định dạng (Pydantic Validation).
        - Trích xuất toàn bộ danh sách các trường bị lỗi và thông báo chi tiết bằng Tiếng Anh.
        - Trả về mã HTTP 422.
        """
        errors = exc.errors()
        parsed_errors = []
        
        for err in errors:
            # Lấy tên trường bị lỗi (bỏ chữ 'body' ở đầu nếu có)
            field = " -> ".join(str(loc) for loc in err.get("loc", []) if loc != "body")
            msg = err.get("msg", "Invalid input data")
            parsed_errors.append({
                "field": field,
                "message": msg
            })

        return JSONResponse(
            status_code=422,
            content={
                "detail": {
                    "code": "VALIDATION_ERROR",
                    "message": "Input validation failed",
                    "errors": parsed_errors,
                }
            },
        )

    @app.exception_handler(HTTPException)
    def http_exception_handler(_: Request, exc: HTTPException):
        """
        Xử lý các lỗi HTTP mặc định của framework Starlette/FastAPI (như 404 Route Not Found, 405 Method Not Allowed).
        - Chuẩn hóa mã lỗi dạng string (NOT_FOUND, METHOD_NOT_ALLOWED).
        """
        if exc.status_code == 404:
            code = "NOT_FOUND"
        elif exc.status_code == 405:
            code = "METHOD_NOT_ALLOWED"
        else:
            code = "HTTP_ERROR"

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": {
                    "code": code,
                    "message": exc.detail,
                }
            },
        )
