from __future__ import annotations

from apps.users.models import User


def get_user_by_phone(*, phone: str) -> User | None:
    return User.objects.filter(phone=phone).first()
