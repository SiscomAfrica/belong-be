from __future__ import annotations

from uuid import UUID

from django.db.models import QuerySet

from apps.audit.models import AuditLog


def list_user_audit_logs(*, actor_id: UUID, limit: int = 50) -> QuerySet[AuditLog]:
    return AuditLog.objects.filter(actor_id=actor_id)[:limit]
