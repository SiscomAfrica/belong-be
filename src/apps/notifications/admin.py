from __future__ import annotations

from django.contrib import admin

from apps.notifications.models import DevicePushToken, Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "title", "is_read", "created_at")
    search_fields = ("title", "body")
    list_filter = ("type", "is_read")
    ordering = ("-created_at",)


@admin.register(DevicePushToken)
class DevicePushTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "platform", "is_active", "created_at")
    list_filter = ("platform", "is_active")
    ordering = ("-created_at",)
