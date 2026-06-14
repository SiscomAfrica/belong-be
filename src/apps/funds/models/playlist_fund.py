from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class PlaylistFund(BaseModel):
    playlist = models.ForeignKey(
        "funds.Playlist",
        on_delete=models.CASCADE,
        related_name="playlist_funds",
    )
    fund = models.ForeignKey(
        "funds.Fund",
        on_delete=models.CASCADE,
        related_name="playlist_entries",
    )
    position = models.PositiveIntegerField(default=0)
    returns_label = models.CharField(
        max_length=100, blank=True, default="Annualised returns",
    )

    class Meta:
        db_table = "funds_playlist_fund"
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["playlist", "fund"],
                name="unique_playlist_fund",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.playlist} - {self.fund} (pos {self.position})"
