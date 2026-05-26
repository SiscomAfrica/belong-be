from __future__ import annotations

import hashlib
import logging
import secrets
from datetime import timedelta

from django.utils import timezone

from apps.authentication.models import OTP
from apps.authentication.selectors.count_active_otps import count_active_otps
from apps.common.exceptions import RateLimitError

logger = logging.getLogger(__name__)

MAX_ACTIVE_OTPS = 3
OTP_EXPIRY_MINUTES = 5


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def send_otp(*, phone: str, purpose: str = "REGISTER", channel: str = "SMS") -> OTP:
    active_count = count_active_otps(phone=phone)
    if active_count >= MAX_ACTIVE_OTPS:
        raise RateLimitError("Too many active OTPs. Please wait before requesting another.")

    raw_code = f"{secrets.randbelow(10**6):06d}"
    otp = OTP.objects.create(
        phone=phone,
        code=_hash_code(raw_code),
        channel=channel,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )

    logger.info("OTP sent to %s for %s (stubbed)", phone, purpose)
    # TODO: integrate SMS provider (Africa's Talking / Twilio)
    logger.debug("OTP code for %s: %s", phone, raw_code)  # noqa: T20

    return otp
