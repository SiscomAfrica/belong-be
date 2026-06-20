from __future__ import annotations

import uuid

from django.db import models


class AuditAction(models.TextChoices):
    USER_REGISTERED = "USER_REGISTERED", "User Registered"
    PIN_SET = "PIN_SET", "PIN Set"
    PIN_CHANGED = "PIN_CHANGED", "PIN Changed"
    OTP_SENT = "OTP_SENT", "OTP Sent"
    OTP_VERIFIED = "OTP_VERIFIED", "OTP Verified"
    KYC_SUBMITTED = "KYC_SUBMITTED", "KYC Submitted"
    KYC_APPROVED = "KYC_APPROVED", "KYC Approved"
    KYC_REJECTED = "KYC_REJECTED", "KYC Rejected"
    INVESTMENT_CREATED = "INVESTMENT_CREATED", "Investment Created"
    INVESTMENT_CONFIRMED = "INVESTMENT_CONFIRMED", "Investment Confirmed"
    INVESTMENT_CANCELLED = "INVESTMENT_CANCELLED", "Investment Cancelled"
    WITHDRAWAL_REQUESTED = "WITHDRAWAL_REQUESTED", "Withdrawal Requested"
    PAYMENT_INITIATED = "PAYMENT_INITIATED", "Payment Initiated"
    PAYMENT_RECEIVED = "PAYMENT_RECEIVED", "Payment Received"
    PAYMENT_FAILED = "PAYMENT_FAILED", "Payment Failed"
    PROFILE_UPDATED = "PROFILE_UPDATED", "Profile Updated"
    TERMS_ACCEPTED = "TERMS_ACCEPTED", "Terms Accepted"
    RECURRING_PLAN_CREATED = "RECURRING_PLAN_CREATED", "Recurring Plan Created"
    RECURRING_PLAN_PAUSED = "RECURRING_PLAN_PAUSED", "Recurring Plan Paused"
    GOAL_CREATED = "GOAL_CREATED", "Goal Created"
    WALLET_CREDITED = "WALLET_CREDITED", "Wallet Credited"
    WALLET_DEBITED = "WALLET_DEBITED", "Wallet Debited"
    NAV_UPDATED = "NAV_UPDATED", "NAV Updated"
    PROFILER_COMPLETED = "PROFILER_COMPLETED", "Profiler Completed"
    REFERRAL_CREATED = "REFERRAL_CREATED", "Referral Created"
    REFERRAL_CONVERTED = "REFERRAL_CONVERTED", "Referral Converted"
    CONSENT_RECORDED = "CONSENT_RECORDED", "Consent Recorded"
    INVESTMENT_KYC_ACTIVATED = "INVESTMENT_KYC_ACTIVATED", "Investment KYC Activated"


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    actor_id = models.UUIDField(null=True, blank=True, db_index=True)
    action = models.CharField(max_length=50, choices=AuditAction.choices, db_index=True)
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField(null=True, blank=True)
    old_values = models.JSONField(default=dict, blank=True)
    new_values = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "audit_log"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs) -> None:  # type: ignore[override]  # noqa: ANN002, ANN003
        if self.pk and AuditLog.objects.filter(pk=self.pk).exists():
            raise ValueError("AuditLog records are immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs) -> None:  # type: ignore[override]  # noqa: ANN002, ANN003
        raise ValueError("AuditLog records cannot be deleted.")

    def __str__(self) -> str:
        return f"{self.action} by {self.actor_id} at {self.created_at}"
