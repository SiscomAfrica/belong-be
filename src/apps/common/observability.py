from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def report_exception(
    *,
    message: str,
    logger_: logging.Logger | None = None,
    **context: Any,
) -> None:
    """Record a failure that was caught and deliberately not re-raised.

    A caught exception that is only logged gets buried in a log file nobody
    reads. Every non-fatal failure path calls this instead, so there is one
    place to attach real alerting when it is wanted — rather than editing a
    dozen scattered except blocks.

    Call from inside an `except` block: `logger.exception` attaches the active
    traceback, which a plain `logger.error` would drop.

    Context values are included as structured log fields. Never pass anything
    that identifies a person or authenticates them — user ids are fine, phone
    numbers, PINs, OTPs and tokens are not.
    """
    (logger_ or logger).exception(message, extra={"failure_context": context})
