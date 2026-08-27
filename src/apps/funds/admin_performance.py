from __future__ import annotations

from django.contrib import admin

from apps.funds.models import FundPerformance


@admin.register(FundPerformance)
class FundPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        "fund", "period", "return_pct",
        "start_value", "end_value", "calculated_at",
    )
    search_fields = ("fund__name",)
    list_filter = ("period",)
    ordering = ("-calculated_at",)
