from __future__ import annotations

from apps.notifications.models import NotificationType
from apps.notifications.services.create_notification import create_notification
from apps.payments.models import StandingOrder, StandingOrderCharge
from apps.payments.providers.ratiba_result import RatibaCallbackResult


def notify_callback(
    *,
    order: StandingOrder,
    charge: StandingOrderCharge,
    result: RatibaCallbackResult,
    is_activation: bool,
) -> None:
    """Tell the user what their standing order just did."""
    if not result.success:
        _notify_failure(order=order, is_activation=is_activation)
        return

    if is_activation:
        # Careful with the wording: the order is live but has collected
        # nothing. Saying money arrived here would be a lie the wallet
        # balance immediately contradicts.
        when = (
            f" The first collection is on {order.first_execution_date:%d %b %Y}."
            if order.first_execution_date
            else ""
        )
        create_notification(
            user_id=order.user_id,
            type=NotificationType.STANDING_ORDER_ACTIVE,
            title="Auto-invest is set up",
            body=f"KSh {charge.amount} will be collected automatically.{when}",
            metadata={"standing_order_id": str(order.id)},
        )
        return

    create_notification(
        user_id=order.user_id,
        type=NotificationType.STANDING_ORDER_CHARGED,
        title="Contribution received",
        body=f"KSh {charge.amount} added to your wallet and ready to invest.",
        metadata={"standing_order_id": str(order.id)},
    )


def _notify_failure(*, order: StandingOrder, is_activation: bool) -> None:
    body = (
        "We could not set up your auto-invest. Please try again."
        if is_activation
        else (
            "We could not collect your scheduled contribution. "
            "We will try again on your next contribution date."
        )
    )
    create_notification(
        user_id=order.user_id,
        type=NotificationType.STANDING_ORDER_FAILED,
        title="Auto-invest deduction failed" if not is_activation else "Auto-invest setup failed",
        body=body,
        metadata={"standing_order_id": str(order.id)},
    )
