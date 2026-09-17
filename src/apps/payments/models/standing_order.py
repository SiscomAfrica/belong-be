from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q

from apps.common.models.base import BaseModel


class StandingOrderStatus(models.TextChoices):
    # Submitted to Daraja and accepted, but the customer has not yet approved
    # the NI Push prompt with their M-PESA PIN. No money moves in this state.
    PENDING = "PENDING", "Pending Authorisation"
    ACTIVE = "ACTIVE", "Active"
    FAILED = "FAILED", "Failed"
    CANCELLED = "CANCELLED", "Cancelled"
    COMPLETED = "COMPLETED", "Completed"


class StandingOrder(BaseModel):
    """An M-Pesa Ratiba standing order backing a recurring investment plan."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="standing_orders",
    )
    recurring_plan = models.ForeignKey(
        "investments.RecurringPlan", on_delete=models.PROTECT,
        related_name="standing_orders",
    )
    # Max 12 alphanumeric characters — a Ratiba constraint, not ours. Sent as
    # AccountReference so a deduction landing on the paybill is attributable
    # even when the callback cannot be correlated any other way.
    account_reference = models.CharField(max_length=12, unique=True, db_index=True)
    standing_order_name = models.CharField(max_length=64)
    # CustomStoId: a UUID we generate and send with the create request. Daraja
    # echoes it back on the callback as BOTH responseRefID and requestRefID,
    # which makes it the one correlation key that does not depend on guessing
    # which field Safaricom populated.
    custom_sto_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    # responseRefID from the synchronous create response. Kept for support
    # traces; it is Safaricom's own id and need not match custom_sto_id.
    response_ref_id = models.CharField(max_length=64, blank=True, default="", db_index=True)
    # reminderScheduleId from the callback — Ratiba's identifier for the
    # standing order itself, which support will ask for.
    reminder_schedule_id = models.CharField(max_length=64, blank=True, default="")
    # firstPaymentReminderDate from the creation callback: when Safaricom
    # expects to collect for the first time. Until then the order is live but
    # has taken nothing, which is what the app needs to tell the customer.
    first_execution_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    frequency = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    phone_number = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20, choices=StandingOrderStatus.choices,
        default=StandingOrderStatus.PENDING, db_index=True,
    )
    failure_reason = models.TextField(blank=True, default="")
    provider_response = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "payments_standing_order"
        ordering = ["-created_at"]
        constraints = [
            # A plan may accumulate cancelled and failed orders over its life,
            # but only ever one that Safaricom might still deduct against.
            models.UniqueConstraint(
                fields=["recurring_plan"],
                condition=Q(status__in=["PENDING", "ACTIVE"]),
                name="unique_live_standing_order_per_plan",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.account_reference} ({self.status})"
