from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class ChargeStatus(models.TextChoices):
    OKAY = "OKAY", "Okay"
    ERROR = "ERROR", "Error"


class ChargeKind(models.TextChoices):
    """What a callback actually reported.

    Daraja sends the same payload shape for both, and both can say
    Status=OKAY with an amount on them — but only one of them is money.
    """

    # The standing order was created and the customer approved the prompt.
    # Carries the order's amount, though nothing has been collected yet.
    ACTIVATION = "ACTIVATION", "Activation"
    # An actual execution against the customer's wallet.
    DEDUCTION = "DEDUCTION", "Deduction"


class StandingOrderCharge(BaseModel):
    """One callback reported against a standing order.

    Append-only and keyed on the transaction id, because Safaricom retries
    callbacks. `transaction_id` being unique is what stops a retry crediting
    the wallet twice — the insert fails and the retry becomes a no-op.
    """

    standing_order = models.ForeignKey(
        "payments.StandingOrder", on_delete=models.PROTECT, related_name="charges",
    )
    kind = models.CharField(max_length=12, choices=ChargeKind.choices, db_index=True)
    # On a deduction this is the M-PESA receipt. On an activation Daraja sends
    # the reminderScheduleId here instead, which is not a receipt at all.
    # Failed attempts report "0000000000", which is not unique, so those are
    # stored with a synthesised key.
    transaction_id = models.CharField(max_length=64, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=10, choices=ChargeStatus.choices, db_index=True)
    response_code = models.CharField(max_length=10, blank=True, default="")
    # Safaricom masks this ("*********867"), so it is for support, not matching.
    masked_msisdn = models.CharField(max_length=32, blank=True, default="")
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "payments_standing_order_charge"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.kind} {self.transaction_id} - {self.amount} - {self.status}"
