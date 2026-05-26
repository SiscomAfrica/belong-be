from __future__ import annotations

from django.contrib import admin

from apps.kyc.models import KYCDocument, KYCSubmission, KYCWebhookLog


@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "status", "document_type", "smile_job_id", "submitted_at")
    search_fields = ("user__phone", "smile_job_id")
    list_filter = ("status", "document_type")
    ordering = ("-created_at",)


@admin.register(KYCDocument)
class KYCDocumentAdmin(admin.ModelAdmin):
    list_display = ("submission", "side", "file_key", "uploaded_at")
    list_filter = ("side",)
    ordering = ("-uploaded_at",)


@admin.register(KYCWebhookLog)
class KYCWebhookLogAdmin(admin.ModelAdmin):
    list_display = ("submission", "result_code", "processed_at", "created_at")
    list_filter = ("result_code",)
    ordering = ("-created_at",)
