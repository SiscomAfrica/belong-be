from __future__ import annotations

from django.db.models import QuerySet

from apps.pools.models import Pool


def list_pools() -> QuerySet[Pool]:
    return Pool.objects.select_related("fund").all()
