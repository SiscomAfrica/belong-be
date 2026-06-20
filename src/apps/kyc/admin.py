from __future__ import annotations

from django.contrib import admin

from apps.kyc.models import KYCDocument, KYCStatus, KYCSubmission, KYCWebhookLog


class KYCDocumentInline(admin.TabularInline):
    model = KYCDocument
    extra = 0
    readonly_fields = ("side", "file_key", "uploaded_at")


@admin.register(KYCSubmission)
class KYCSubmissionAdmin(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "status", "document_type", "submitted_at")
    search_fields = ("user__phone", "first_name", "last_name", "id_number")
    list_filter = ("status", "document_type")
    ordering = ("-created_at",)
    readonly_fields = ("user", "smile_job_id", "submitted_at", "result_text", "created_at", "updated_at")
    inlines = [KYCDocumentInline]
    actions = ["approve_kyc", "reject_kyc"]
    fieldsets = (
        (None, {"fields": ("user", "status", "document_type")}),
        ("Personal Information", {"fields": (
            "first_name", "last_name", "date_of_birth",
            "nationality", "id_number", "kra_pin",
        )}),
        ("Residential & Financial", {"fields": (
            "city", "address", "employment_status", "income_source",
        )}),
        ("Next of Kin", {"fields": ("kin_name", "kin_phone", "kin_email")}),
        ("Verification", {"fields": ("smile_job_id", "submitted_at", "result_text")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    @admin.action(description="Approve selected KYC submissions")
    def approve_kyc(self, request, queryset):  # noqa: ANN001, ANN201
        reviewable = [KYCStatus.PENDING, KYCStatus.MANUAL_REVIEW]
        count = queryset.filter(status__in=reviewable).update(status=KYCStatus.VERIFIED)
        self.message_user(request, f"{count} submission(s) approved.")

    @admin.action(description="Reject selected KYC submissions")
    def reject_kyc(self, request, queryset):  # noqa: ANN001, ANN201
        reviewable = [KYCStatus.PENDING, KYCStatus.MANUAL_REVIEW]
        count = queryset.filter(status__in=reviewable).update(status=KYCStatus.REJECTED)
        self.message_user(request, f"{count} submission(s) rejected.")


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
