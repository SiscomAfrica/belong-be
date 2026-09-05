from __future__ import annotations

from datetime import timedelta

from django.db.models import F
from django.utils import timezone

from apps.authentication.models import OTP
from apps.authentication.models.otp import OTPPurpose
from apps.authentication.otp_hashing import hash_otp_code
from apps.common.exceptions import OTPExpiredError, OTPMaxAttemptsError, ValidationError

MAX_OTP_ATTEMPTS = 5

# The app verifies the code on its own screen and only collects the new PIN
# afterwards, so by the time a reset arrives the OTP is already `is_used`.
# Matching on `is_used=False` the way `verify_otp` does would therefore reject
# every legitimate reset. The code is instead accepted for a short window after
# it was issued; `reset_pin` deletes the row on success, so a code still only
# ever sets one PIN.
RESET_WINDOW_MINUTES = 15

# The app requests a LOGIN OTP for the forgot-passcode flow. RESET_PIN is
# accepted as well so the client can move to the purpose that actually names
# the operation without needing a coordinated backend release.
RESET_PURPOSES = (OTPPurpose.LOGIN, OTPPurpose.RESET_PIN)


def consume_reset_otp(*, phone: str, code: str) -> OTP:
    """Check a reset code against the newest one issued to this phone.

    Returns the matching row without deleting it — the caller deletes it under
    a lock once the new PIN has actually been written, so a failed PIN
    validation leaves the code usable for a retry.
    """
    otp = _recent_otp(phone=phone)
    if otp is None:
        raise OTPExpiredError("No recent code found. Please request a new one.")

    if otp.attempts >= MAX_OTP_ATTEMPTS:
        raise OTPMaxAttemptsError("Maximum verification attempts exceeded.")

    # Counted in SQL rather than in Python: two guesses arriving together must
    # not both read the same attempt count and overwrite each other's increment.
    # `.update()` skips `save()`, so `auto_now` has to be applied by hand.
    OTP.objects.filter(pk=otp.pk).update(
        attempts=F("attempts") + 1,
        updated_at=timezone.now(),
    )
    otp.refresh_from_db(fields=["attempts"])

    if hash_otp_code(code) != otp.code:
        remaining = max(MAX_OTP_ATTEMPTS - otp.attempts, 0)
        raise ValidationError(f"Invalid code. {remaining} attempts remaining.")

    return otp


def _recent_otp(*, phone: str) -> OTP | None:
    """The newest code issued to this phone inside the reset window."""
    cutoff = timezone.now() - timedelta(minutes=RESET_WINDOW_MINUTES)
    return (
        OTP.objects.filter(
            phone=phone,
            purpose__in=RESET_PURPOSES,
            created_at__gte=cutoff,
        )
        .order_by("-created_at")
        .first()
    )
