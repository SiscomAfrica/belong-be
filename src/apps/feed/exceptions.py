from __future__ import annotations

from apps.common.exceptions import (
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)


class FeedPostNotFoundError(NotFoundError):
    code = "FEED_POST_NOT_FOUND"

    def __init__(self) -> None:
        super().__init__("Feed post not found.")


class FeedPostOwnershipError(PermissionDeniedError):
    code = "FEED_POST_NOT_OWNER"

    def __init__(self) -> None:
        super().__init__("You do not own this feed post.")


class FeedPostEditWindowClosedError(ValidationError):
    """Distinct from an ownership failure: it is their post, just too old.

    Separated so the app can say so, and so a client that hid its edit button
    on a stale window gets a message that makes sense rather than being told
    the post is not theirs.
    """

    code = "FEED_POST_EDIT_WINDOW_CLOSED"

    def __init__(self, minutes: int) -> None:
        super().__init__(
            f"Posts can only be edited within {minutes} minutes of posting."
            if minutes
            else "Posts cannot be edited after they are shared.",
        )


class FeedPostSelfReportError(ValidationError):
    """Reporting your own post is not a moderation signal.

    Separate from an ownership error, which says the opposite thing — here it
    *is* yours, and the answer is to delete it rather than flag it.
    """

    code = "FEED_POST_SELF_REPORT"

    def __init__(self) -> None:
        super().__init__("This is your own post — delete it instead.")
