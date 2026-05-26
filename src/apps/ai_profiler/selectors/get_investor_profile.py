from __future__ import annotations

from uuid import UUID

from apps.ai_profiler.exceptions import ProfileNotFoundError
from apps.ai_profiler.models import InvestorProfile


def get_investor_profile(*, user_id: UUID) -> InvestorProfile:
    try:
        return InvestorProfile.objects.get(user_id=user_id)
    except InvestorProfile.DoesNotExist:
        raise ProfileNotFoundError() from None
