from __future__ import annotations

from django.contrib import admin

from apps.common.admin_mixins import HeroImageAdminMixin
from apps.funds.models import Fund, FundNAV, FundPerformance


@admin.register(Fund)
class FundAdmin(HeroImageAdminMixin, admin.ModelAdmin):
    list_display = (
        "name", "fund_type", "category", "risk_level",
        "currency", "is_trending", "is_active",
        "hero_image_preview", "created_at",
    )
    search_fields = ("name", "slug")
    list_filter = ("fund_type", "category", "risk_level", "is_trending", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("hero_image_preview",)
    ordering = ("-created_at",)
    fieldsets = (
        (None, {"fields": (
            "name", "slug", "ticker_symbol", "description",
            "fund_type", "category", "risk_level", "currency",
        )}),
        ("Financials", {"fields": (
            "minimum_investment", "lock_in_days",
            "projected_annual_return", "effective_annual_yield",
            "annualized_daily_yield", "expense_ratio", "aum", "ytd_return",
        )}),
        ("Details", {"fields": (
            "launched_date", "management_type", "listed_country",
            "fund_manager", "top_holdings", "perfect_for",
        )}),
        ("Hero Image", {"fields": (
            "hero_image", "hero_image_url", "hero_image_preview",
        )}),
        ("Display", {"fields": (
            "chart_url", "emoji", "is_trending", "is_active", "metadata",
        )}),
    )


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
