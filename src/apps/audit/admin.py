from __future__ import annotations

from django.contrib import admin

from apps.audit.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor_id", "entity_type", "entity_id", "created_at")
    list_filter = ("action", "entity_type")
    search_fields = ("actor_id", "entity_id")
    ordering = ("-created_at",)
    readonly_fields = (
        "id", "created_at", "actor_id", "action", "entity_type",
        "entity_id", "old_values", "new_values", "ip_address", "metadata",
    )

    def has_add_permission(self, request) -> bool:  # noqa: ANN001
        return False

    def has_change_permission(self, request, obj=None) -> bool:  # noqa: ANN001
        return False

    def has_delete_permission(self, request, obj=None) -> bool:  # noqa: ANN001
        return False
