from __future__ import annotations

from django.utils import timezone

from apps.common.exceptions import ValidationError
from apps.users.models import User


def accept_terms(*, user: User, accepted: bool) -> User:
    if not accepted:
        raise ValidationError("Terms must be accepted")

    user.terms_accepted_at = timezone.now()
    user.save(update_fields=["terms_accepted_at", "updated_at"])
    return user
