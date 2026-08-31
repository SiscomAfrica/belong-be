from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel
from apps.users.models.user import InvestorType


class ProfileTemplate(BaseModel):
    investor_type = models.CharField(
        max_length=20,
        choices=InvestorType.choices,
        unique=True,
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, db_index=True)
    accent = models.CharField(max_length=50, default="investor.")
    badge_label = models.CharField(max_length=50)
    description = models.TextField()
    section_title = models.CharField(max_length=100, default="Hand picked jams")
    section_action = models.CharField(max_length=100, default="Tap any to Invest")
    playlist = models.ForeignKey(
        "funds.Playlist",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profile_templates",
        help_text="Materialised cache of the funds matching this profile's criteria",
    )
    centroid = models.JSONField(
        default=dict,
        blank=True,
        help_text="Target anchor per ordinal behaviour; matching is nearest centroid",
    )
    risk_band = models.JSONField(
        default=list,
        blank=True,
        help_text="[min, max] Fund.risk_level this profile may be recommended",
    )
    category_weights = models.JSONField(
        default=dict,
        blank=True,
        help_text="Fund category to weight, used to rank within the risk band",
    )
    max_funds = models.PositiveSmallIntegerField(default=3)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "ai_profiler_profile_template"
        ordering = ["position"]

    def __str__(self) -> str:
        return self.name
