from __future__ import annotations

from uuid import UUID

from django.utils import timezone

from apps.audit.models.audit_log import AuditAction
from apps.audit.services.create_audit_log import create_audit_log
from apps.compliance.models import UserConsent


def record_consent(
    *,
    user_id: UUID,
    consent_version_id: UUID,
    ip_address: str | None = None,
) -> UserConsent:
    consent = UserConsent.objects.create(
        user_id=user_id,
        consent_version_id=consent_version_id,
        accepted_at=timezone.now(),
        ip_address=ip_address,
    )

    create_audit_log(
        action=AuditAction.CONSENT_RECORDED,
        actor_id=user_id,
        entity_type="UserConsent",
        entity_id=consent.id,
        new_values={"consent_version_id": str(consent_version_id)},
    )

    return consent
