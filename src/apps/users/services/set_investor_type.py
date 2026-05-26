from __future__ import annotations

from apps.common.exceptions import ValidationError
from apps.users.models import User
from apps.users.models.user import InvestorType


def set_investor_type(*, user: User, investor_type: str) -> User:
    valid = {c.value for c in InvestorType}
    if investor_type not in valid:
        raise ValidationError(f"Invalid investor type: {investor_type}")

    user.investor_type = investor_type
    user.save(update_fields=["investor_type", "updated_at"])
    return user
