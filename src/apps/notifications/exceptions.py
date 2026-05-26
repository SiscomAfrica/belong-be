from __future__ import annotations

from apps.common.exceptions import NotFoundError


class NotificationNotFoundError(NotFoundError):
    code = "NOTIFICATION_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Notification not found.")
