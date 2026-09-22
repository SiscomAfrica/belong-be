from __future__ import annotations

import logging

from ninja_jwt.tokens import RefreshToken

from apps.authentication.services.set_pin import set_pin
from apps.authentication.services.verify_otp import verify_otp
from apps.common.exceptions import ConflictError
from apps.common.observability import report_exception
from apps.common.validation import (
    validate_mobile_e164,
    validate_otp_code,
    validate_referral_code,
)
from apps.users.selectors.get_user_by_phone import get_user_by_phone
from apps.users.services.create_user import create_user

logger = logging.getLogger(__name__)


def register(
    *, phone: str, otp_code: str, pin: str, referred_by_code: str = ""
) -> dict[str, str]:
    # Normalised before the uniqueness check, or the same subscriber can hold
    # two accounts by typing 0712345678 once and +254712345678 the next time.
    phone = validate_mobile_e164(value=phone)
    otp_code = validate_otp_code(value=otp_code)
    referred_by_code = validate_referral_code(value=referred_by_code)

    existing = get_user_by_phone(phone=phone)
    if existing is not None:
        raise ConflictError("User with this phone already exists.")

    verify_otp(phone=phone, code=otp_code, purpose="REGISTER")
    user = create_user(phone=phone)
    set_pin(user=user, pin=pin)

    if referred_by_code:
        _try_create_referral(referrer_code=referred_by_code, user_id=user.id)

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


def _try_create_referral(*, referrer_code: str, user_id) -> None:
    try:
        from apps.referrals.services.create_referral import create_referral

        create_referral(referrer_code=referrer_code, referred_user_id=user_id)
    except Exception:
        # Registration has succeeded; a bad referral code must not block it.
        report_exception(
            message="Referral creation failed during registration",
            logger_=logger,
            referrer_code=referrer_code,
        )
