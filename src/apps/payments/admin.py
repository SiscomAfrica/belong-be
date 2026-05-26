from __future__ import annotations

from django.contrib import admin

from apps.payments.models import PaymentTransaction, Wallet, WithdrawalRequest


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "provider", "status", "amount", "created_at")
    list_filter = ("provider", "status")
    search_fields = ("external_ref", "merchant_request_id")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "amount", "status", "created_at")
    list_filter = ("status",)
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance_ksh", "balance_usd", "updated_at")
    search_fields = ("user__phone_number",)
    readonly_fields = ("id", "created_at", "updated_at")
