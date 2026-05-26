from __future__ import annotations

from apps.users.models import User


def enable_biometrics(*, user: User, enable: bool = True) -> User:
    user.biometrics_enabled = enable
    user.save(update_fields=["biometrics_enabled", "updated_at"])
    return user
