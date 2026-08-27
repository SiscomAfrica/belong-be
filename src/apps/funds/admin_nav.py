from __future__ import annotations

from django.contrib import admin

from apps.funds.models import FundNAV


@admin.register(FundNAV)
class FundNAVAdmin(admin.ModelAdmin):
    list_display = ("fund", "date", "nav_value", "daily_change_pct", "created_at")
    search_fields = ("fund__name",)
    list_filter = ("date",)
    ordering = ("-date",)
