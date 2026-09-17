from __future__ import annotations

from datetime import date, datetime

from apps.payments.models import StandingOrder, StandingOrderStatus
from apps.payments.providers.ratiba_result import RatibaCallbackResult


def _parse_daraja_date(raw: str) -> date | None:
    """Daraja sends dates as yyyymmdd strings."""
    try:
        return datetime.strptime(raw, "%Y%m%d").date()  # noqa: DTZ007
    except (ValueError, TypeError):
        return None


def activate_standing_order(
    *, order: StandingOrder, result: RatibaCallbackResult,
) -> StandingOrder:
    """Record that the customer approved the prompt and the order is live.

    No money has moved. Daraja's creation callback reports the order's Amount
    and Status=OKAY, but the first execution does not happen until StartDate.
    """
    order.status = StandingOrderStatus.ACTIVE
    # Ratiba's own id for the order, which support asks for.
    order.reminder_schedule_id = result.reminder_schedule_id
    first = _parse_daraja_date(result.first_payment_date)
    if first is not None:
        order.first_execution_date = first

    order.save(update_fields=[
        "status", "reminder_schedule_id", "first_execution_date", "updated_at",
    ])
    return order


def fail_standing_order(
    *, order: StandingOrder, result: RatibaCallbackResult,
) -> StandingOrder:
    """The prompt was declined, cancelled, or never reached the customer."""
    order.status = StandingOrderStatus.FAILED
    order.failure_reason = f"{result.response_code}: {result.description}".strip(": ")
    order.save(update_fields=["status", "failure_reason", "updated_at"])
    return order
