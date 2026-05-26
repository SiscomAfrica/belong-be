from __future__ import annotations

from uuid import UUID

from apps.audit.models import AuditLog


def create_audit_log(
    *,
    action: str,
    entity_type: str,
    actor_id: UUID | None = None,
    entity_id: UUID | None = None,
    old_values: dict | None = None,
    new_values: dict | None = None,
    ip_address: str | None = None,
    metadata: dict | None = None,
) -> AuditLog:
    return AuditLog.objects.create(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        old_values=old_values or {},
        new_values=new_values or {},
        ip_address=ip_address,
        metadata=metadata or {},
    )
