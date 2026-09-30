class AppError(Exception):
    """Base Exception for the entire application."""

    def __init__(
        self,
        error_message: str = "An unexpected error occurred",
        error_code: str = "INTERNAL_SERVER_ERROR",
        status_code: int = 500,
        detail: str | None = None,
    ):
        message = detail if detail is not None else error_message
        self.error_message = message
        self.error_code = error_code
        self.status_code = status_code
        self.detail = message  # Alias for backward compatibility
        super().__init__(self.error_message)


class NotFoundError(AppError):
    """404 Not Found - When a resource is not found"""

    def __init__(
        self,
        error_message: str = "Resource not found",
        error_code: str = "NOT_FOUND",
        detail: str | None = None,
    ):
        super().__init__(
            error_message=detail if detail is not None else error_message,
            error_code=error_code,
            status_code=404,
        )


class BadRequestError(AppError):
    """400 Bad Request - Invalid inputs or business logic violation"""

    def __init__(
        self,
        error_message: str = "Bad request",
        error_code: str = "BAD_REQUEST",
        detail: str | None = None,
    ):
        super().__init__(
            error_message=detail if detail is not None else error_message,
            error_code=error_code,
            status_code=400,
        )


class UnauthorizedError(AppError):
    """401 Unauthorized - Authentication failed or token expired/invalid"""

    def __init__(
        self,
        error_message: str = "Unauthorized access",
        error_code: str = "UNAUTHORIZED",
        detail: str | None = None,
    ):
        super().__init__(
            error_message=detail if detail is not None else error_message,
            error_code=error_code,
            status_code=401,
        )


class ForbiddenError(AppError):
    """403 Forbidden - Authenticated but lacks permissions"""

    def __init__(
        self,
        error_message: str = "Permission denied",
        error_code: str = "FORBIDDEN",
        detail: str | None = None,
    ):
        super().__init__(
            error_message=detail if detail is not None else error_message,
            error_code=error_code,
            status_code=403,
        )


class ConflictError(AppError):
    """409 Conflict - Resource already exists (e.g. Email exists)"""

    def __init__(
        self,
        error_message: str = "Resource already exists",
        error_code: str = "CONFLICT",
        detail: str | None = None,
    ):
        super().__init__(
            error_message=detail if detail is not None else error_message,
            error_code=error_code,
            status_code=409,
        )


class TooManyRequestsError(AppError):
    """429 Too Many Requests - Rate limit exceeded"""

    def __init__(
        self,
        error_message: str = "Too many requests. Please slow down.",
        error_code: str = "TOO_MANY_REQUESTS",
        detail: str | None = None,
    ):
        super().__init__(
            error_message=detail if detail is not None else error_message,
            error_code=error_code,
            status_code=429,
        )


class BadGatewayError(AppError):
    """502 Bad Gateway - External service failed"""

    def __init__(
        self,
        error_message: str = "Bad gateway",
        error_code: str = "BAD_GATEWAY",
        detail: str | None = None,
    ):
        super().__init__(
            error_message=detail if detail is not None else error_message,
            error_code=error_code,
            status_code=502,
        )
