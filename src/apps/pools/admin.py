from __future__ import annotations

from django.contrib import admin

from apps.pools.models import Pool


@admin.register(Pool)
class PoolAdmin(admin.ModelAdmin):
    list_display = ("fund", "total_units", "total_aum", "nav_per_unit", "updated_at")
    search_fields = ("fund__name",)
    readonly_fields = ("id", "created_at", "updated_at")
