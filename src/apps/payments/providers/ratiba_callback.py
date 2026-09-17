from __future__ import annotations

from decimal import Decimal, InvalidOperation

from apps.payments.providers.ratiba_result import RatibaCallbackResult

# Ratiba is inconsistent about casing between its payload shapes: the create
# response uses `ResponseHeader`/`ResponseBody` with code "200", callbacks use
# `responseHeader`/`responseBody` with code "0", and the error callback
# switches back and capitalises the `Name`/`Value` pairs too. Header lookups
# are therefore case-insensitive.
#
# responseData is the exception. It carries BOTH `status` (the standing
# order's state, "ACTIVE") and `Status` (this delivery's outcome, "OKAY") —
# two different fields separated only by case — so those are read exactly and
# only fall back to a loose match.
_FAILED_TRANSACTION_ID = "0000000000"


def _ci_get(data: dict, key: str) -> object:
    lowered = key.lower()
    for k, v in data.items():
        if k.lower() == lowered:
            return v
    return None


def _as_dict(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def _data_pairs(body: dict) -> tuple[dict[str, str], dict[str, str]]:
    """Flatten responseData into (exact-case, lowercased) lookups."""
    rows = _ci_get(body, "responseData")
    if not isinstance(rows, list):
        return {}, {}

    exact: dict[str, str] = {}
    lower: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = _ci_get(row, "name")
        if isinstance(name, str):
            value = str(_ci_get(row, "value") or "")
            exact[name] = value
            lower[name.lower()] = value
    return exact, lower


def _to_decimal(raw: str) -> Decimal | None:
    # Through str() and never float() — a deduction is money.
    try:
        return Decimal(raw)
    except (InvalidOperation, ValueError):
        return None


def parse_ratiba_callback(*, payload: dict) -> RatibaCallbackResult:
    header = _as_dict(_ci_get(payload, "responseHeader"))
    body = _as_dict(_ci_get(payload, "responseBody"))
    exact, lower = _data_pairs(body)

    delivery = (exact.get("Status") or lower.get("status", "")).upper()
    # The authoritative code is the one inside responseData; the header code
    # describes the delivery, not the deduction.
    code = lower.get("responsecode") or str(_ci_get(header, "responseCode") or "")
    txn_id = lower.get("transactionid", "")
    amount_raw = lower.get("amount", "")

    return RatibaCallbackResult(
        request_ref_id=str(_ci_get(header, "requestRefID") or ""),
        response_ref_id=str(_ci_get(header, "responseRefID") or ""),
        account_reference=lower.get("accountreference", ""),
        transaction_id="" if txn_id == _FAILED_TRANSACTION_ID else txn_id,
        reminder_schedule_id=lower.get("reminderscheduleid", ""),
        first_payment_date=lower.get("firstpaymentreminderdate", ""),
        order_status=exact.get("status", ""),
        response_code=code,
        description=str(_ci_get(header, "responseDescription") or ""),
        masked_msisdn=lower.get("msisdn", ""),
        success=delivery == "OKAY" and code == "0",
        amount=_to_decimal(amount_raw) if amount_raw else None,
        raw_data=payload,
    )
