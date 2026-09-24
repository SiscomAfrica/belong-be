from __future__ import annotations

from apps.common.exceptions import ConflictError, NotFoundError


class SessionNotFoundError(NotFoundError):
    code = "SESSION_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Conversation session not found.")


class SessionAlreadyCompletedError(ConflictError):
    code = "SESSION_ALREADY_COMPLETED"

    def __init__(self) -> None:
        super().__init__("Session has already been completed.")


class ProfileNotFoundError(NotFoundError):
    code = "PROFILE_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Investor profile not found.")


class ProviderRateLimitedError(Exception):
    """The model provider is refusing calls for now.

    Distinct from a generation failure because the response is different:
    a malformed answer is worth retrying, a 429 is not. Retrying immediately
    against a rate limiter only deepens the hole, and the pool refill was
    doing it ninety times a run.
    """

    def __init__(self, retry_after: int | None = None) -> None:
        self.retry_after = retry_after
        super().__init__(
            f"Provider rate limited; retry after {retry_after}s"
            if retry_after
            else "Provider rate limited",
        )
