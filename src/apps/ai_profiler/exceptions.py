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
