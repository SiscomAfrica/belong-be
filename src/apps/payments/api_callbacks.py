from __future__ import annotations

import json

from django.http import HttpRequest
from ninja import Router

from apps.payments.schemas import WebhookAckOut
from apps.payments.services.process_c2b_confirmation import process_c2b_confirmation
from apps.payments.services.process_mpesa_callback import process_mpesa_callback
from apps.payments.services.process_paystack_webhook import process_paystack_webhook
from apps.payments.services.process_ratiba_callback import process_ratiba_callback

callbacks_router = Router(tags=["callbacks"], auth=None)


@callbacks_router.post("/mpesa/", response=WebhookAckOut, auth=None)
def mpesa_callback(request: HttpRequest):
    """Receive and process M-Pesa payment result callbacks."""
    payload = json.loads(request.body)
    process_mpesa_callback(payload=payload)
    return WebhookAckOut(result_code=0, result_desc="Accepted")


@callbacks_router.post("/ratiba/", response=WebhookAckOut, auth=None)
def ratiba_callback(request: HttpRequest):
    """Receive M-Pesa Ratiba standing-order deduction results.

    Always acknowledges. Safaricom retries anything it does not see a 200 for,
    and the handler is idempotent on the M-PESA receipt, so a retry is cheaper
    than a failed delivery.
    """
    payload = json.loads(request.body)
    process_ratiba_callback(payload=payload)
    return WebhookAckOut(result_code=0, result_desc="Accepted")


@callbacks_router.post("/c2b/confirmation/", response={200: dict}, auth=None)
def c2b_confirmation(request: HttpRequest):
    """Receive completed paybill payments, M-Pesa Ratiba executions included.

    Always acknowledges with ResultCode 0. Safaricom retries anything else,
    and the handler is idempotent on the M-PESA receipt, so a retry is cheaper
    than a failed delivery.
    """
    payload = json.loads(request.body)
    process_c2b_confirmation(payload=payload)
    return 200, {"ResultCode": 0, "ResultDesc": "Accepted"}


@callbacks_router.post("/c2b/validation/", response={200: dict}, auth=None)
def c2b_validation(request: HttpRequest):
    """Accept every payment offered.

    Only called when external validation is switched on for the shortcode.
    Rejecting here would bounce a customer's money back, so this accepts and
    leaves attribution to the confirmation handler.
    """
    return 200, {"ResultCode": 0, "ResultDesc": "Accepted"}


@callbacks_router.post("/paystack/", response={200: dict}, auth=None)
def paystack_webhook(request: HttpRequest):
    """Receive and process Paystack webhook events."""
    signature = request.headers.get("x-paystack-signature", "")
    body = request.body
    payload = json.loads(body)
    process_paystack_webhook(payload=payload, signature=signature, body=body)
    return 200, {"status": "ok"}
