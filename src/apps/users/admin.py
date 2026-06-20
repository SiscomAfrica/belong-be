from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.urls import reverse
from django.utils.html import format_html

from apps.users.models import User, UserDevice


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("phone", "first_name", "investor_type", "is_onboarded", "kyc_status", "created_at")
    search_fields = ("phone", "first_name", "last_name")
    list_filter = ("investor_type", "is_onboarded", "biometrics_enabled")
    ordering = ("-created_at",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Belong", {"fields": (
            "phone", "pin_hash", "biometrics_enabled", "investor_type",
            "preferred_currency", "is_onboarded", "terms_accepted_at", "referral_code",
        )}),
    )

    def get_queryset(self, request):  # noqa: ANN001, ANN201
        return super().get_queryset(request).select_related("kyc_submission")

    @admin.display(description="KYC")
    def kyc_status(self, obj):  # noqa: ANN001, ANN201
        if not hasattr(obj, "kyc_submission") or obj.kyc_submission is None:
            return "\u2014"
        sub = obj.kyc_submission
        url = reverse("admin:kyc_kycsubmission_change", args=[sub.pk])
        return format_html('<a href="{}">{}</a>', url, sub.status)


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ("user", "device_id", "platform", "is_active", "created_at")
    list_filter = ("platform", "is_active")
    search_fields = ("device_id",)
