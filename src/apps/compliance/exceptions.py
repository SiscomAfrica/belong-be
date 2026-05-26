from __future__ import annotations

from apps.common.exceptions import NotFoundError, ValidationError


class InvestmentLimitExceededError(ValidationError):
    code = "INVESTMENT_LIMIT_EXCEEDED"

    def __init__(self, message: str = "Investment limit exceeded.") -> None:
        super().__init__(message)


class ConsentRequiredError(ValidationError):
    code = "CONSENT_REQUIRED"

    def __init__(self) -> None:
        super().__init__("Consent acceptance is required.")


class StatementNotFoundError(NotFoundError):
    code = "STATEMENT_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Statement not found for the given period.")
