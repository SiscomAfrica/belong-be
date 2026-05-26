from __future__ import annotations

import hashlib
import hmac

import httpx
from django.conf import settings

from apps.kyc.exceptions import KYCProviderError
from apps.kyc.providers.base import BaseKYCProvider, KYCCallbackResult, KYCInitResult

SANDBOX_URL = "https://testapi.smileidentity.com"
PRODUCTION_URL = "https://api.smileidentity.com"


class SmileIdentityProvider(BaseKYCProvider):
    def _get_base_url(self) -> str:
        if getattr(settings, "SMILE_IDENTITY_ENV", "sandbox") == "production":
            return PRODUCTION_URL
        return SANDBOX_URL

    def submit_verification(
        self, *, partner_params: dict, images: list[dict],
    ) -> KYCInitResult:
        url = f"{self._get_base_url()}/v1/upload"
        payload = {
            "partner_id": settings.SMILE_IDENTITY_PARTNER_ID,
            "api_key": settings.SMILE_IDENTITY_API_KEY,
            "partner_params": partner_params,
            "images": images,
            "callback_url": settings.SMILE_IDENTITY_CALLBACK_URL,
        }
        try:
            resp = httpx.post(url, json=payload, timeout=30)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            raise KYCProviderError(f"Smile Identity API failed: {e}") from e
        data = resp.json()
        return KYCInitResult(
            job_id=data.get("smile_job_id", ""),
            upload_url=data.get("upload_url", ""),
            raw_response=data,
        )

    def verify_callback(self, *, payload: dict) -> KYCCallbackResult:
        result = payload.get("result", payload)
        result_code = str(result.get("ResultCode", ""))
        return KYCCallbackResult(
            job_id=str(result.get("SmileJobID", payload.get("smile_job_id", ""))),
            success=result_code == "0100",
            result_code=result_code,
            result_text=result.get("ResultText", ""),
            raw_data=payload,
        )

    @staticmethod
    def verify_signature(*, payload: str, signature: str) -> bool:
        api_key = getattr(settings, "SMILE_IDENTITY_API_KEY", "")
        expected = hmac.new(
            api_key.encode(), payload.encode(), hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
