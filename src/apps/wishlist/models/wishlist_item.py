from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.common.models.base import BaseModel


class WishlistItem(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )
    fund = models.ForeignKey(
        "funds.Fund",
        on_delete=models.CASCADE,
        related_name="wishlist_items",
    )

    class Meta:
        db_table = "wishlist_item"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "fund"],
                name="unique_user_fund_wishlist",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} - {self.fund_id}"
