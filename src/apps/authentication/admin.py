from __future__ import annotations

from django.contrib import admin

from apps.authentication.models import OTP


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("phone", "purpose", "channel", "is_used", "attempts", "expires_at")
    list_filter = ("purpose", "channel", "is_used")
    search_fields = ("phone",)
    ordering = ("-created_at",)
    readonly_fields = ("code", "created_at", "updated_at")
