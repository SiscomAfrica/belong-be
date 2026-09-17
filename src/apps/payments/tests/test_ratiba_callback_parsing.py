from __future__ import annotations

from decimal import Decimal

from apps.payments.providers.ratiba_callback import parse_ratiba_callback

# Verbatim from Daraja's published Ratiba samples. The casing differences are
# the point of these tests, not transcription slips: the success callback uses
# `responseHeader`, the error one `ResponseHeader`.
SUCCESS = {
    "responseHeader": {
        "responseRefID": "06aae68f-7d5a-4b44-a22d-8aa77126689b",
        "requestRefID": "06aae68f-7d5a-4b44-a22d-8aa77126689b",
        "responseCode": "0",
        "responseDescription": "Standing order created successfully",
    },
    "responseBody": {
        "responseData": [
            {"name": "standingOrderName", "value": "mpesa_Ratiba_test_Name"},
            {"name": "amount", "value": "500.00"},
            {"name": "issuePaymentReminderUntil", "value": "20280407"},
            {"name": "reminderScheduleId", "value": "2571168"},
            {"name": "firstPaymentReminderDate", "value": "20260807"},
            {"name": "status", "value": "ACTIVE"},
            {"name": "TransactionID", "value": "2571168"},
            {"name": "ResponseCode", "value": "0"},
            {"name": "Status", "value": "OKAY"},
            {"name": "Msisdn", "value": "*********867"},
        ],
    },
}

ERROR = {
    "ResponseHeader": {
        "responseRefID": "4dd9b5d9-d738-42ba-9326-2cc99e966000",
        "requestRefID": "c8c2bb31-3b3a-402e-84fc-21ef35161e48",
        "responseCode": "1037",
        "responseDescription": "Error",
    },
    "ResponseBody": {
        "ResponseData": [
            {"Name": "TransactionID", "Value": "0000000000"},
            {"Name": "responseCode", "Value": "1037"},
            {"Name": "Status", "Value": "ERROR"},
            {"Name": "Msisdn", "Value": "*********149"},
        ],
    },
}


def test_success_callback_is_parsed() -> None:
    result = parse_ratiba_callback(payload=SUCCESS)

    assert result.success is True
    assert result.transaction_id == "2571168"
    assert result.response_code == "0"
    assert result.reminder_schedule_id == "2571168"
    assert result.masked_msisdn == "*********867"
    # The CustomStoId we sent, echoed back on both ref fields. This is what
    # makes a callback attributable without guessing.
    assert result.request_ref_id == "06aae68f-7d5a-4b44-a22d-8aa77126689b"
    assert result.response_ref_id == result.request_ref_id


def test_the_two_status_fields_are_not_confused() -> None:
    """`status` is the order's state; `Status` is this delivery's outcome.

    They differ only by case. Flattening them together made the parse depend
    on which happened to come last in the array.
    """
    result = parse_ratiba_callback(payload=SUCCESS)

    assert result.order_status == "ACTIVE"
    assert result.success is True


def test_error_callback_is_parsed_despite_the_capitalised_keys() -> None:
    result = parse_ratiba_callback(payload=ERROR)

    assert result.success is False
    assert result.response_code == "1037"
    assert result.request_ref_id == "c8c2bb31-3b3a-402e-84fc-21ef35161e48"


def test_the_failure_sentinel_is_not_treated_as_a_receipt() -> None:
    """"0000000000" is sent to every failing customer, so it identifies nobody."""
    assert parse_ratiba_callback(payload=ERROR).transaction_id == ""


def test_the_amount_is_read_as_decimal() -> None:
    result = parse_ratiba_callback(payload=SUCCESS)

    assert result.amount == Decimal("500.00")
    assert isinstance(result.amount, Decimal)


def test_garbage_payload_does_not_raise() -> None:
    result = parse_ratiba_callback(payload={"unexpected": "shape"})

    assert result.success is False
