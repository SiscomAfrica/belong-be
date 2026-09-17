from __future__ import annotations

from datetime import date
from decimal import ROUND_DOWN, Decimal
from uuid import UUID

from django.conf import settings

from apps.payments.exceptions import PaymentProviderError

# Ratiba's own Frequency codes, per Daraja's parameter table. Kept here rather
# than on PlanFrequency so the investments app stays ignorant of the wire
# format.
#
# Note 4 is Bi-weekly and 5 is Monthly. An earlier draft of this file had a
# shorter table that made 4 Monthly — that would have scheduled every monthly
# plan fortnightly, deducting roughly twice as often as the customer agreed.
FREQUENCY_CODES = {
    "ONE_OFF": "1",
    "DAILY": "2",
    "WEEKLY": "3",
    "BIWEEKLY": "4",
    "MONTHLY": "5",
    "BIMONTHLY": "6",
    "QUARTERLY": "7",
    "HALF_YEARLY": "8",
    "YEARLY": "9",
}

PAYBILL = "4"
TILL = "2"
_TRANSACTION_TYPES = {
    PAYBILL: "Standing Order Pay Bill Ext-Third Party",
    TILL: "Standing Order Merchant Payment Ext-Third Party",
}


def ratiba_amount(amount: Decimal) -> str:
    """Ratiba accepts whole numbers only.

    Rounds down, so a plan never deducts more than the user agreed to; the
    remainder stays in the plan amount and surfaces in wallet reconciliation
    rather than being silently collected.
    """
    return str(amount.quantize(Decimal("1"), rounding=ROUND_DOWN))


def build_create_payload(
    *,
    name: str,
    amount: Decimal,
    phone_number: str,
    frequency: str,
    start: date,
    end: date,
    account_reference: str,
    description: str,
    custom_sto_id: UUID,
) -> dict[str, str]:
    code = FREQUENCY_CODES.get(frequency)
    if code is None:
        msg = f"Frequency {frequency} has no M-Pesa Ratiba equivalent."
        raise PaymentProviderError(msg)

    receiver_type = getattr(settings, "MPESA_RATIBA_RECEIVER_TYPE", PAYBILL)
    return {
        "StandingOrderName": name,
        "StartDate": start.strftime("%Y%m%d"),
        "EndDate": end.strftime("%Y%m%d"),
        "BusinessShortCode": str(settings.MPESA_RATIBA_SHORTCODE),
        "TransactionType": _TRANSACTION_TYPES.get(
            receiver_type, _TRANSACTION_TYPES[PAYBILL]
        ),
        "ReceiverPartyIdentifierType": receiver_type,
        # Ours, not Safaricom's: Daraja echoes this back on the callback as
        # both responseRefID and requestRefID, which makes it the one
        # correlation key we can count on.
        "CustomStoId": str(custom_sto_id),
        "Amount": ratiba_amount(amount),
        "PartyA": phone_number,
        "CallBackURL": f"{settings.MPESA_CALLBACK_BASE_URL}/api/callbacks/ratiba/",
        # Both fields are length-capped by Safaricom; truncating here keeps a
        # long fund name from failing the whole request.
        "AccountReference": account_reference[:12],
        "TransactionDesc": description[:13],
        "Frequency": code,
    }
