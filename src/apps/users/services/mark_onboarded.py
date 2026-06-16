from __future__ import annotations

from apps.users.models import User


def mark_onboarded(*, user: User) -> User:
    if user.is_onboarded:
        return user

    user.is_onboarded = True
    user.save(update_fields=["is_onboarded", "updated_at"])
    return user
