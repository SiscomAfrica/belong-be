from __future__ import annotations

import bcrypt

from apps.common.validation.credentials import (
    PIN_MAX_LENGTH,
    PIN_MIN_LENGTH,
    validate_pin,
)
from apps.users.models import User

__all__ = ["PIN_MAX_LENGTH", "PIN_MIN_LENGTH", "set_pin"]


def set_pin(*, user: User, pin: str) -> User:
    # Bounded before bcrypt sees it: hashing is deliberately slow, so an
    # unbounded PIN on an unauthenticated endpoint is free CPU to burn.
    cleaned = validate_pin(value=pin)

    user.pin_hash = bcrypt.hashpw(cleaned.encode(), bcrypt.gensalt()).decode()
    user.save(update_fields=["pin_hash", "updated_at"])
    return user
