from __future__ import annotations

from django.contrib import admin

from apps.funds.models import Fund, FundNAV, FundPerformance


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = (
        "name", "fund_type", "category", "risk_level",
        "currency", "is_trending", "is_active", "created_at",
    )
    search_fields = ("name", "slug")
    list_filter = ("fund_type", "category", "risk_level", "is_trending", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("-created_at",)


@admin.register(FundNAV)
class FundNAVAdmin(admin.ModelAdmin):
    list_display = ("fund", "date", "nav_value", "daily_change_pct", "created_at")
    search_fields = ("fund__name",)
    list_filter = ("date",)
    ordering = ("-date",)


@admin.register(FundPerformance)
class FundPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        "fund", "period", "return_pct",
        "start_value", "end_value", "calculated_at",
    )
    search_fields = ("fund__name",)
    list_filter = ("period",)
    ordering = ("-calculated_at",)
