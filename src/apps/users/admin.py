from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.users.models import User, UserDevice


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("phone", "first_name", "investor_type", "is_onboarded", "created_at")
    search_fields = ("phone", "first_name", "last_name")
    list_filter = ("investor_type", "is_onboarded", "biometrics_enabled")
    ordering = ("-created_at",)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Belong", {"fields": (
            "phone", "pin_hash", "biometrics_enabled", "investor_type",
            "preferred_currency", "is_onboarded", "terms_accepted_at", "referral_code",
        )}),
    )


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ("user", "device_id", "platform", "is_active", "created_at")
    list_filter = ("platform", "is_active")
    search_fields = ("device_id",)
