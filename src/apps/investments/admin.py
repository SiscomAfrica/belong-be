from __future__ import annotations

from django.contrib import admin

from apps.investments.models import (
    Holding,
    Investment,
    InvestmentGoal,
    PortfolioSnapshot,
    RecurringPlan,
)


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ("user", "fund", "amount", "units", "status", "confirmed_at", "created_at")
    search_fields = ("user__phone_number", "idempotency_key")
    list_filter = ("status", "fund")
    ordering = ("-created_at",)
    readonly_fields = ("idempotency_key",)


@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    list_display = ("user", "fund", "total_units", "total_invested", "average_nav", "created_at")
    search_fields = ("user__phone_number",)
    list_filter = ("fund",)
    ordering = ("-created_at",)


@admin.register(PortfolioSnapshot)
class PortfolioSnapshotAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "total_value", "total_invested", "daily_change", "created_at")
    search_fields = ("user__phone_number",)
    list_filter = ("date",)
    ordering = ("-date",)


@admin.register(RecurringPlan)
class RecurringPlanAdmin(admin.ModelAdmin):
    list_display = ("user", "fund", "amount", "frequency", "next_run_date", "is_active")
    list_filter = ("frequency", "is_active")
    ordering = ("-created_at",)


@admin.register(InvestmentGoal)
class InvestmentGoalAdmin(admin.ModelAdmin):
    list_display = ("user", "fund", "target_amount", "target_date", "created_at")
    list_filter = ("fund",)
    ordering = ("-created_at",)
