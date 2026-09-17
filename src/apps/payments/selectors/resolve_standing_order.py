from __future__ import annotations

from uuid import UUID

from apps.payments.models import StandingOrder
from apps.payments.providers.ratiba_result import RatibaCallbackResult


def _as_uuid(value: str) -> UUID | None:
    try:
        return UUID(value)
    except (ValueError, AttributeError, TypeError):
        return None


def resolve_standing_order(*, result: RatibaCallbackResult) -> StandingOrder | None:
    """Find the standing order a callback belongs to.

    Daraja echoes the CustomStoId we generated on the create request back as
    both `responseRefID` and `requestRefID`, so either one identifies the row
    outright — no guessing which field Safaricom filled in. AccountReference
    is a last resort for a delivery that carries neither.
    """
    for ref in (result.request_ref_id, result.response_ref_id):
        sto_id = _as_uuid(ref)
        if sto_id is None:
            continue
        order = StandingOrder.objects.filter(custom_sto_id=sto_id).first()
        if order is not None:
            return order

    if result.account_reference:
        return StandingOrder.objects.filter(
            account_reference=result.account_reference,
        ).first()

    return None
