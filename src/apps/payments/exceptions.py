from __future__ import annotations

from apps.common.exceptions import AppError, ConflictError, NotFoundError, ValidationError


class PaymentProviderError(AppError):
    status_code = 502
    code = "PAYMENT_PROVIDER_ERROR"

    def __init__(self, message: str = "Payment provider error.") -> None:
        super().__init__(message)


class PaymentAlreadyInitiatedError(ConflictError):
    code = "PAYMENT_ALREADY_INITIATED"

    def __init__(self) -> None:
        super().__init__("A payment has already been initiated for this investment.")


class PaymentNotFoundError(NotFoundError):
    code = "PAYMENT_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Payment transaction not found.")


class InvalidCallbackError(ValidationError):
    code = "INVALID_CALLBACK"

    def __init__(self, message: str = "Invalid callback payload.") -> None:
        super().__init__(message)


class InvestmentNotPendingError(ValidationError):
    code = "INVESTMENT_NOT_PENDING"

    def __init__(self) -> None:
        super().__init__("Investment is not in PENDING status.")


class InsufficientBalanceError(ValidationError):
    code = "INSUFFICIENT_BALANCE"

    def __init__(self) -> None:
        super().__init__("Insufficient wallet balance.")
