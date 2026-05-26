from __future__ import annotations

from django.db.models import QuerySet

from apps.audit.models import AuditLog


def list_audit_logs(*, action: str | None = None, limit: int = 50) -> QuerySet[AuditLog]:
    qs = AuditLog.objects.all()
    if action is not None:
        qs = qs.filter(action=action)
    return qs[:limit]
