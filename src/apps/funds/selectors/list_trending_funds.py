from __future__ import annotations

from django.db.models import QuerySet

from apps.funds.models import Fund


def list_trending_funds() -> QuerySet[Fund]:
    return Fund.objects.filter(is_trending=True, is_active=True)
