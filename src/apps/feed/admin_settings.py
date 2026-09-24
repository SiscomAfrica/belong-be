from __future__ import annotations

from django.contrib import admin

from apps.feed.models import FeedSettings


@admin.register(FeedSettings)
class FeedSettingsAdmin(admin.ModelAdmin):
    """Single-row feed configuration, following InvestmentSettings.

    A second row would make which one wins a matter of ordering, and deleting
    the only row would silently fall back to the field default, so neither is
    offered.
    """

    list_display = ("edit_window_minutes", "updated_at")

    def has_add_permission(self, request, obj=None) -> bool:
        return not FeedSettings.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
