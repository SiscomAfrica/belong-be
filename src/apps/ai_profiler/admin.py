from __future__ import annotations

from django.contrib import admin

from apps.ai_profiler.models import ConversationMessage, ConversationSession, InvestorProfile


@admin.register(ConversationSession)
class ConversationSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__phone",)
    ordering = ("-created_at",)


@admin.register(ConversationMessage)
class ConversationMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "role", "created_at")
    list_filter = ("role",)
    ordering = ("created_at",)


@admin.register(InvestorProfile)
class InvestorProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "risk_tolerance", "time_horizon", "created_at")
    search_fields = ("user__phone",)
    ordering = ("-created_at",)
