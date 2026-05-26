from __future__ import annotations

import bcrypt

from apps.common.exceptions import AuthenticationError
from apps.users.models import User


def verify_pin(*, user: User, pin: str) -> bool:
    if not user.pin_hash:
        raise AuthenticationError("PIN not set. Please set your PIN first.")

    if not bcrypt.checkpw(pin.encode(), user.pin_hash.encode()):
        raise AuthenticationError("Invalid PIN.")

    return True
