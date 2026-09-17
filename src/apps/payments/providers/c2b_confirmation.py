from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation


@dataclass
class C2BConfirmation:
    """One completed payment into the paybill.

    This is how an M-Pesa Ratiba execution reaches us: the standing order pays
    the shortcode like any other customer would, carrying the AccountReference
    we set at creation as BillRefNumber. The Ratiba callback itself only ever
    reports the creation result.
    """

    trans_id: str = ""
    bill_ref: str = ""
    amount: Decimal | None = None
    msisdn: str = ""
    short_code: str = ""
    trans_time: str = ""
    raw_data: dict = field(default_factory=dict)


def _get(payload: dict, *names: str) -> str:
    """Read the first present key, tolerating Daraja's casing drift."""
    lowered = {k.lower(): v for k, v in payload.items()}
    for name in names:
        value = lowered.get(name.lower())
        if value not in (None, ""):
            return str(value)
    return ""


def parse_c2b_confirmation(*, payload: dict) -> C2BConfirmation:
    raw_amount = _get(payload, "TransAmount", "Amount")
    try:
        # Through str() and never float() — this is money.
        amount = Decimal(raw_amount) if raw_amount else None
    except (InvalidOperation, ValueError):
        amount = None

    return C2BConfirmation(
        trans_id=_get(payload, "TransID", "TransactionID"),
        # BillRefNumber is the account number the payer quoted. For a Ratiba
        # execution that is the AccountReference we generated.
        bill_ref=_get(payload, "BillRefNumber", "AccountReference").strip(),
        amount=amount,
        msisdn=_get(payload, "MSISDN", "Msisdn"),
        short_code=_get(payload, "BusinessShortCode", "ShortCode"),
        trans_time=_get(payload, "TransTime"),
        raw_data=payload,
    )
