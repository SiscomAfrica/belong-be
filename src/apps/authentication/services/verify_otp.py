from __future__ import annotations

from django.db import transaction

from apps.authentication.models import OTP, OTPPurpose
from apps.authentication.otp_hashing import hash_otp_code
from apps.authentication.selectors.get_active_otp import get_active_otp
from apps.common.exceptions import OTPExpiredError, OTPMaxAttemptsError, ValidationError
from apps.common.validation import validate_mobile_e164, validate_otp_code
from apps.common.validation.choice import validate_choice

MAX_OTP_ATTEMPTS = 5


def verify_otp(*, phone: str, code: str, purpose: str = "REGISTER") -> OTP:
    # Shape-checked before the lookup so a malformed code cannot consume one
    # of the five attempts a real guess is allowed.
    phone = validate_mobile_e164(value=phone)
    code = validate_otp_code(value=code, field="code")
    purpose = validate_choice(value=purpose, allowed=OTPPurpose, field="purpose")

    candidate = get_active_otp(phone=phone, purpose=purpose)
    if candidate is None:
        raise OTPExpiredError("No active OTP found. Please request a new one.")

    return _consume_under_lock(pk=candidate.pk, code=code)


def _consume_under_lock(*, pk, code: str) -> OTP:
    """Spend one attempt against a locked row.

    This is a read -> decide -> act sequence, so a lock is the only thing that
    makes the attempt cap real. Counting with F() alone still leaves the
    check-then-act: two guesses arriving together both read attempts=4, both
    pass the cap, and the attacker gets a sixth and seventh try. Six guesses
    instead of five does not matter much on its own — but the same race run
    wide gives unbounded tries at a six-digit code, which is the whole account.
    """
    with transaction.atomic():
        otp = OTP.objects.select_for_update().filter(pk=pk).first()
        if otp is None:
            raise OTPExpiredError("No active OTP found. Please request a new one.")

        if otp.is_used:
            # Claimed by whichever request won the lock first.
            raise OTPExpiredError("This code has already been used.")

        if otp.attempts >= MAX_OTP_ATTEMPTS:
            otp.is_used = True
            otp.save(update_fields=["is_used", "updated_at"])
            raise OTPMaxAttemptsError("Maximum verification attempts exceeded.")

        otp.attempts += 1

        if hash_otp_code(code) != otp.code:
            otp.save(update_fields=["attempts", "updated_at"])
            remaining = MAX_OTP_ATTEMPTS - otp.attempts
            raise ValidationError(
                f"Invalid OTP code. {remaining} attempts remaining.",
            )

        otp.is_used = True
        otp.save(update_fields=["is_used", "attempts", "updated_at"])
        return otp
