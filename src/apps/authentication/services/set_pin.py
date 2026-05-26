from __future__ import annotations

import bcrypt

from apps.common.exceptions import ValidationError
from apps.users.models import User

PIN_MIN_LENGTH = 4
PIN_MAX_LENGTH = 6


def set_pin(*, user: User, pin: str) -> User:
    if not pin.isdigit() or not (PIN_MIN_LENGTH <= len(pin) <= PIN_MAX_LENGTH):
        raise ValidationError(f"PIN must be {PIN_MIN_LENGTH}-{PIN_MAX_LENGTH} digits.")

    user.pin_hash = bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
    user.save(update_fields=["pin_hash", "updated_at"])
    return user
