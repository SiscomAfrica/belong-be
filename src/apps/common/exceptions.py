from __future__ import annotations


class AppError(Exception):
    status_code: int = 400
    code: str = "APP_ERROR"
    details: dict = {}  # noqa: RUF012

    def __init__(self, message: str = "", *, details: dict | None = None) -> None:
        self.message = message
        if details is not None:
            self.details = details
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class ValidationError(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"


class PermissionDeniedError(AppError):
    status_code = 403
    code = "PERMISSION_DENIED"


class ConflictError(AppError):
    status_code = 409
    code = "CONFLICT"


class AuthenticationError(AppError):
    status_code = 401
    code = "AUTHENTICATION_ERROR"


class OTPExpiredError(AppError):
    status_code = 400
    code = "OTP_EXPIRED"


class OTPMaxAttemptsError(AppError):
    status_code = 429
    code = "OTP_MAX_ATTEMPTS"


class RateLimitError(AppError):
    status_code = 429
    code = "RATE_LIMIT_EXCEEDED"
