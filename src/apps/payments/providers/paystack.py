from __future__ import annotations

import hashlib
import hmac
from decimal import Decimal

import httpx
from django.conf import settings

from apps.payments.exceptions import InvalidCallbackError, PaymentProviderError
from apps.payments.providers.base import (
    BasePaymentProvider,
    ProviderCallbackResult,
    ProviderInitResult,
)

PAYSTACK_API = "https://api.paystack.co"


class PaystackProvider(BasePaymentProvider):
    def _headers(self) -> dict:
        return {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}

    def initiate_payment(
        self, *, amount: Decimal, phone_number: str, reference: str,
    ) -> ProviderInitResult:
        url = f"{PAYSTACK_API}/transaction/initialize"
        payload = {
            "amount": int(amount * 100),
            "reference": reference,
            "currency": "KES",
        }
        try:
            resp = httpx.post(
                url, json=payload, headers=self._headers(), timeout=30,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise PaymentProviderError(f"Paystack init failed: {e}") from e
        data = resp.json()
        if not data.get("status"):
            raise PaymentProviderError(data.get("message", "Paystack init failed"))
        return ProviderInitResult(
            external_ref=data["data"]["reference"],
            authorization_url=data["data"]["authorization_url"],
            raw_response=data,
        )

    def verify_callback(self, *, payload: dict) -> ProviderCallbackResult:
        data = payload.get("data", {})
        ref = data.get("reference", "")
        status = data.get("status", "")
        amount = Decimal(str(data.get("amount", 0))) / 100
        return ProviderCallbackResult(
            external_ref=ref,
            success=status == "success",
            amount=amount,
            failure_reason="" if status == "success" else f"Status: {status}",
            raw_data=payload,
        )

    @staticmethod
    def verify_signature(*, payload_body: bytes, signature: str) -> bool:
        expected = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode(),
            payload_body,
            hashlib.sha512,
        ).hexdigest()
        if not hmac.compare_digest(expected, signature):
            raise InvalidCallbackError("Invalid Paystack signature.")
        return True
