from __future__ import annotations

from django.contrib import admin

from apps.market_data.models import ExchangeRate, MarketTicker


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ("base_currency", "quote_currency", "rate", "source", "fetched_at")
    list_filter = ("base_currency", "source")
    search_fields = ("base_currency", "quote_currency")
    ordering = ("base_currency", "quote_currency")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(MarketTicker)
class MarketTickerAdmin(admin.ModelAdmin):
    list_display = ("symbol", "name", "price", "change_pct", "currency", "fetched_at")
    list_filter = ("currency",)
    search_fields = ("symbol", "name")
    ordering = ("symbol",)
    readonly_fields = ("id", "created_at", "updated_at")
