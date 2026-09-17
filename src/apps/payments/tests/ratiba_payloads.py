from __future__ import annotations


def creation(*, ref: str, ok: bool = True) -> dict:
    """Daraja's documented callback: the standing order was set up.

    Reports Status=OKAY and the order's Amount, but nothing is collected until
    StartDate. TransactionID is the reminderScheduleId, not an M-PESA receipt.
    """
    return {
        "responseHeader": {
            "responseRefID": ref,
            "requestRefID": ref,
            "responseCode": "0" if ok else "1032",
            "responseDescription": (
                "Standing order created successfully" if ok else "Error"
            ),
        },
        "responseBody": {
            "responseData": [
                {"name": "standingOrderName", "value": "Belong BLTESTREF01"},
                {"name": "amount", "value": "500.00"},
                {"name": "reminderScheduleId", "value": "2571168"},
                {"name": "firstPaymentReminderDate", "value": "20260807"},
                {"name": "status", "value": "ACTIVE" if ok else "FAILED"},
                {"name": "TransactionID", "value": "2571168" if ok else "0000000000"},
                {"name": "ResponseCode", "value": "0" if ok else "1032"},
                {"name": "Status", "value": "OKAY" if ok else "ERROR"},
            ],
        },
    }


def execution(*, ref: str, receipt: str = "SC8F2IQMH5") -> dict:
    """An actual deduction against the customer's wallet."""
    payload = creation(ref=ref)
    payload["responseBody"]["responseData"] = [
        {"name": "amount", "value": "500.00"},
        {"name": "TransactionID", "value": receipt},
        {"name": "ResponseCode", "value": "0"},
        {"name": "Status", "value": "OKAY"},
    ]
    return payload
