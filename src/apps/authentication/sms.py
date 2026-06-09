from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

TILIL_URL = "https://api.tililtech.com/sms/v3/sendsms"


@dataclass(frozen=True)
class SMSResult:
    success: bool
    message_id: str = ""
    status_desc: str = ""


def send_sms(*, phone: str, message: str) -> SMSResult:
    if not settings.SMS_ENABLED:
        logger.info("SMS disabled — skipping send to %s", phone)
        return SMSResult(success=True, status_desc="disabled")

    payload = {
        "api_key": settings.SMS_API_KEY,
        "service_id": settings.SMS_SERVICE_ID,
        "mobile": phone,
        "response_type": "json",
        "shortcode": settings.SMS_SHORTCODE,
        "message": message,
    }
    try:
        resp = httpx.post(TILIL_URL, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        first = data[0] if isinstance(data, list) else data
        ok = first.get("status_code") == "1000"
        return SMSResult(
            success=ok,
            message_id=first.get("message_id", ""),
            status_desc=first.get("status_desc", ""),
        )
    except Exception:
        logger.exception("SMS send failed for %s", phone)
        return SMSResult(success=False, status_desc="request_failed")
