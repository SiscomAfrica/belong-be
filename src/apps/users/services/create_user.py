from __future__ import annotations

import secrets
import string

from apps.users.models import User


def _generate_referral_code(*, length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def create_user(*, phone: str) -> User:
    referral_code = _generate_referral_code()
    while User.objects.filter(referral_code=referral_code).exists():
        referral_code = _generate_referral_code()

    return User.objects.create(
        phone=phone,
        username=phone,
        referral_code=referral_code,
    )
