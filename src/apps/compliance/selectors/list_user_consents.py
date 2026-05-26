from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.compliance.models import UserConsent


def list_user_consents(*, user_id: UUID) -> QuerySet[UserConsent]:
    return (
        UserConsent.objects.filter(user_id=user_id)
        .select_related("consent_version")
        .order_by("-accepted_at")
    )
