from __future__ import annotations

import logging

from ninja_jwt.tokens import RefreshToken

from apps.authentication.services.set_pin import set_pin
from apps.authentication.services.verify_otp import verify_otp
from apps.common.exceptions import ConflictError
from apps.users.selectors.get_user_by_phone import get_user_by_phone
from apps.users.services.create_user import create_user

logger = logging.getLogger(__name__)


def register(
    *, phone: str, otp_code: str, pin: str, referred_by_code: str = ""
) -> dict[str, str]:
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
        logger.warning("Failed to create referral for code %s", referrer_code)
