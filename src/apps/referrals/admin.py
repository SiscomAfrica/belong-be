from __future__ import annotations

from django.contrib import admin

from apps.referrals.models import CredsLedger, Referral


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("id", "referrer", "referred_user", "status", "creds_awarded", "created_at")
    list_filter = ("status",)
    search_fields = ("referrer__phone", "referred_user__phone")
    ordering = ("-created_at",)


@admin.register(CredsLedger)
class CredsLedgerAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "delta", "reason", "balance_after", "created_at")
    search_fields = ("user__phone",)
    ordering = ("-created_at",)
