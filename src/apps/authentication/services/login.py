from __future__ import annotations

import bcrypt

from ninja_jwt.tokens import RefreshToken

from apps.common.exceptions import AuthenticationError
from apps.users.selectors.get_user_by_phone import get_user_by_phone


def login(*, phone: str, pin: str) -> dict[str, str]:
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
