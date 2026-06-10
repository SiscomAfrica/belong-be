from __future__ import annotations

import json

from django.http import HttpRequest
from ninja import Router

from apps.payments.schemas import WebhookAckOut
from apps.payments.services.process_mpesa_callback import process_mpesa_callback
from apps.payments.services.process_paystack_webhook import process_paystack_webhook

callbacks_router = Router(tags=["callbacks"], auth=None)


@callbacks_router.post("/mpesa/", response=WebhookAckOut, auth=None)
def mpesa_callback(request: HttpRequest):
    """Receive and process M-Pesa payment result callbacks."""
    payload = json.loads(request.body)
    process_mpesa_callback(payload=payload)
    return WebhookAckOut(result_code=0, result_desc="Accepted")


@callbacks_router.post("/paystack/", response={200: dict}, auth=None)
def paystack_webhook(request: HttpRequest):
    """Receive and process Paystack webhook events."""
    signature = request.headers.get("x-paystack-signature", "")
    body = request.body
    payload = json.loads(body)
    process_paystack_webhook(payload=payload, signature=signature, body=body)
    return 200, {"status": "ok"}
