from __future__ import annotations

from ninja import NinjaAPI
from ninja.errors import Throttled

from apps.common.exceptions import AppError
from apps.common.schemas import ErrorOut
from config.throttle_messages import throttle_message


def register_exception_handlers(api: NinjaAPI) -> None:
    """Map internal exceptions onto the documented error envelope.

    Every error the API returns has the same shape, so clients switch on
    `error.code` rather than parsing prose.
    """

    @api.exception_handler(Throttled)
    def handle_throttled(request, exc: Throttled):
        """Say which limit was hit and when it lifts.

        Ninja's default body is a bare "Too many requests.", which tells a user
        who has just tried to move money nothing about whether to wait a minute
        or half a day.
        """
        wait = int(exc.wait) if exc.wait else None
        return api.create_response(
            request,
            ErrorOut(
                error={
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": throttle_message(
                        path=request.path, wait_seconds=wait,
                    ),
                    "details": {"retry_after_seconds": wait} if wait else {},
                },
            ).dict(),
            status=429,
        )

    @api.exception_handler(AppError)
    def handle_app_error(request, exc: AppError):
        return api.create_response(
            request,
            ErrorOut(
                error={"code": exc.code, "message": str(exc), "details": exc.details},
            ).dict(),
            status=exc.status_code,
        )
