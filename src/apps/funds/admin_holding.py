from __future__ import annotations

from django.contrib import admin

from apps.funds.models import FundHolding


class FundHoldingInline(admin.TabularInline):
    model = FundHolding
    extra = 1
    fields = ("name", "logo_image", "logo_url", "position")
    readonly_fields = ("logo_url",)
    ordering = ("position",)


@admin.register(FundHolding)
class FundHoldingAdmin(admin.ModelAdmin):
    list_display = ("name", "fund", "position", "logo_url", "created_at")
    search_fields = ("name", "fund__name")
    list_filter = ("fund",)
    readonly_fields = ("logo_url",)
    ordering = ("fund", "position")
