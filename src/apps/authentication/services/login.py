from __future__ import annotations

import bcrypt
from ninja_jwt.tokens import RefreshToken

from apps.common.exceptions import AuthenticationError, ValidationError
from apps.common.validation import validate_mobile_e164, validate_pin
from apps.users.selectors.get_user_by_phone import get_user_by_phone


def login(*, phone: str, pin: str) -> dict[str, str]:
    # A malformed credential is reported as a failed login, not as a
    # validation error: telling an attacker "that PIN is the wrong shape"
    # confirms the phone exists and narrows the search space for the rest.
    try:
        phone = validate_mobile_e164(value=phone)
        pin = validate_pin(value=pin)
    except ValidationError:
        raise AuthenticationError("Invalid phone number or PIN.") from None

    user = get_user_by_phone(phone=phone)
    if user is None or not user.is_active:
        raise AuthenticationError("Invalid phone number or PIN.")

    if not user.pin_hash:
        raise AuthenticationError("PIN not set. Please set your PIN first.")

    if not bcrypt.checkpw(pin.encode(), user.pin_hash.encode()):
        raise AuthenticationError("Invalid phone number or PIN.")

    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }
