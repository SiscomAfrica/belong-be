from __future__ import annotations

from django.contrib import admin

from apps.compliance.models import ConsentVersion, InvestmentLimit, UserConsent


@admin.register(InvestmentLimit)
class InvestmentLimitAdmin(admin.ModelAdmin):
    list_display = ("kyc_tier", "max_per_transaction", "max_per_month")
    ordering = ("kyc_tier",)


@admin.register(ConsentVersion)
class ConsentVersionAdmin(admin.ModelAdmin):
    list_display = ("document_type", "version", "effective_date", "content_url")
    list_filter = ("document_type",)
    ordering = ("-effective_date",)


@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    list_display = ("user", "consent_version", "accepted_at", "ip_address")
    search_fields = ("user__phone",)
    ordering = ("-accepted_at",)
