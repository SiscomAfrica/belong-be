from __future__ import annotations

from apps.common.exceptions import AppError, ConflictError, NotFoundError, ValidationError


class KYCAlreadySubmittedError(ConflictError):
    code = "KYC_ALREADY_SUBMITTED"

    def __init__(self) -> None:
        super().__init__("KYC verification is already submitted or verified.")


class KYCNotFoundError(NotFoundError):
    code = "KYC_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("KYC submission not found.")


class KYCInvalidStateError(ValidationError):
    code = "KYC_INVALID_STATE"

    def __init__(self, message: str = "Invalid KYC state for this operation.") -> None:
        super().__init__(message)


class KYCProviderError(AppError):
    status_code = 502
    code = "KYC_PROVIDER_ERROR"

    def __init__(self, message: str = "KYC provider error.") -> None:
        super().__init__(message)
