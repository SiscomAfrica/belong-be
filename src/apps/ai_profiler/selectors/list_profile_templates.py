from __future__ import annotations

from django.db.models import QuerySet

from apps.ai_profiler.models import ProfileTemplate


def list_profile_templates() -> QuerySet[ProfileTemplate]:
    return (
        ProfileTemplate.objects.filter(is_active=True)
        .select_related("playlist")
        .prefetch_related("playlist__playlist_funds__fund")
        .order_by("position")
    )
