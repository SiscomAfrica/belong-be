from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class RatibaCallbackResult:
    """One parsed M-Pesa Ratiba callback."""

    # Both carry the CustomStoId we sent on the create request.
    request_ref_id: str = ""
    response_ref_id: str = ""
    account_reference: str = ""
    transaction_id: str = ""
    # Ratiba's own identifier for the standing order.
    reminder_schedule_id: str = ""
    # yyyymmdd. When the first execution is due — creation callback only.
    first_payment_date: str = ""
    # The standing order's lifecycle state, e.g. "ACTIVE". Distinct from
    # `success`, which is this one delivery's outcome.
    order_status: str = ""
    response_code: str = ""
    description: str = ""
    masked_msisdn: str = ""
    success: bool = False
    amount: Decimal | None = None
    raw_data: dict = field(default_factory=dict)
