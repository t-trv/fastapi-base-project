class AppError(Exception):
    """Base Exception for the entire application."""

    def __init__(
        self,
        detail: str = "An unexpected error occurred",
        status_code: int = 500,
        error_code: str = "INTERNAL_SERVER_ERROR",
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.detail)


class NotFoundError(AppError):
    """404 Not Found - When a resource (User, Camera, v.v.) is not found"""

    def __init__(
        self, detail: str = "Resource not found", error_code: str = "NOT_FOUND"
    ):
        super().__init__(detail=detail, status_code=404, error_code=error_code)


class BadRequestError(AppError):
    """400 Bad Request - Invalid inputs or business logic violation"""

    def __init__(self, detail: str = "Bad request", error_code: str = "BAD_REQUEST"):
        super().__init__(detail=detail, status_code=400, error_code=error_code)


class UnauthorizedError(AppError):
    """401 Unauthorized - Authentication failed or token expired/invalid"""

    def __init__(
        self, detail: str = "Unauthorized access", error_code: str = "UNAUTHORIZED"
    ):
        super().__init__(detail=detail, status_code=401, error_code=error_code)


class ForbiddenError(AppError):
    """403 Forbidden - Authenticated but lacks permissions"""

    def __init__(
        self, detail: str = "Permission denied", error_code: str = "FORBIDDEN"
    ):
        super().__init__(detail=detail, status_code=403, error_code=error_code)


class ConflictError(AppError):
    """409 Conflict - Resource already exists (e.g. Email exists)"""

    def __init__(
        self, detail: str = "Resource already exists", error_code: str = "CONFLICT"
    ):
        super().__init__(detail=detail, status_code=409, error_code=error_code)
