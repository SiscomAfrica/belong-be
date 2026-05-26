from __future__ import annotations

import base64
from datetime import datetime
from decimal import Decimal

import httpx
from django.conf import settings
from django.core.cache import cache

from apps.payments.exceptions import PaymentProviderError
from apps.payments.providers.base import (
    BasePaymentProvider,
    ProviderCallbackResult,
    ProviderInitResult,
)

SANDBOX_URL = "https://sandbox.safaricom.co.ke"
PRODUCTION_URL = "https://api.safaricom.co.ke"


class MpesaProvider(BasePaymentProvider):
    def _get_base_url(self) -> str:
        if getattr(settings, "MPESA_ENV", "sandbox") == "production":
            return PRODUCTION_URL
        return SANDBOX_URL

    def _get_access_token(self) -> str:
        cached = cache.get("mpesa_access_token")
        if cached:
            return cached
        url = f"{self._get_base_url()}/oauth/v1/generate?grant_type=client_credentials"
        try:
            resp = httpx.get(
                url,
                auth=(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
                timeout=30,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise PaymentProviderError(f"M-Pesa auth failed: {e}") from e
        token = resp.json()["access_token"]
        cache.set("mpesa_access_token", token, timeout=3300)
        return token

    def _generate_password(self, timestamp: str) -> str:
        data = f"{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}"
        return base64.b64encode(data.encode()).decode()

    def initiate_payment(
        self, *, amount: Decimal, phone_number: str, reference: str,
    ) -> ProviderInitResult:
        token = self._get_access_token()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")  # noqa: DTZ005
        password = self._generate_password(timestamp)
        url = f"{self._get_base_url()}/mpesa/stkpush/v1/processrequest"
        payload = {
            "BusinessShortCode": settings.MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,
            "PartyB": settings.MPESA_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": f"{settings.MPESA_CALLBACK_BASE_URL}/api/callbacks/mpesa/",
            "AccountReference": reference[:12],
            "TransactionDesc": "Belong Investment",
        }
        try:
            resp = httpx.post(
                url, json=payload,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise PaymentProviderError(f"M-Pesa STK push failed: {e}") from e
        data = resp.json()
        if data.get("ResponseCode") != "0":
            raise PaymentProviderError(data.get("ResponseDescription", "STK push failed"))
        return ProviderInitResult(
            external_ref=data["CheckoutRequestID"],
            merchant_request_id=data.get("MerchantRequestID", ""),
            raw_response=data,
        )

    def verify_callback(self, *, payload: dict) -> ProviderCallbackResult:
        cb = payload.get("Body", {}).get("stkCallback", {})
        return ProviderCallbackResult(
            external_ref=cb.get("CheckoutRequestID", ""),
            success=cb.get("ResultCode") == 0,
            failure_reason=cb.get("ResultDesc", "") if cb.get("ResultCode") != 0 else "",
            raw_data=payload,
        )
