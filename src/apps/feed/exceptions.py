from __future__ import annotations

from apps.common.exceptions import NotFoundError, PermissionDeniedError


class FeedPostNotFoundError(NotFoundError):
    code = "FEED_POST_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Feed post not found.")


class FeedPostOwnershipError(PermissionDeniedError):
    code = "FEED_POST_NOT_OWNER"

    def __init__(self) -> None:
        super().__init__("You do not own this feed post.")
