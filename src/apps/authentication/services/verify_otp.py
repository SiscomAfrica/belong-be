from __future__ import annotations

import hashlib

from apps.authentication.models import OTP
from apps.authentication.selectors.get_active_otp import get_active_otp
from apps.common.exceptions import OTPExpiredError, OTPMaxAttemptsError, ValidationError

MAX_OTP_ATTEMPTS = 5


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def verify_otp(*, phone: str, code: str, purpose: str = "REGISTER") -> OTP:
    otp = get_active_otp(phone=phone, purpose=purpose)
    if otp is None:
        raise OTPExpiredError("No active OTP found. Please request a new one.")

    if otp.attempts >= MAX_OTP_ATTEMPTS:
        otp.is_used = True
        otp.save(update_fields=["is_used", "updated_at"])
        raise OTPMaxAttemptsError("Maximum verification attempts exceeded.")

    otp.attempts += 1

    if _hash_code(code) != otp.code:
        otp.save(update_fields=["attempts", "updated_at"])
        remaining = MAX_OTP_ATTEMPTS - otp.attempts
        raise ValidationError(f"Invalid OTP code. {remaining} attempts remaining.")

    otp.is_used = True
    otp.save(update_fields=["is_used", "attempts", "updated_at"])
    return otp
