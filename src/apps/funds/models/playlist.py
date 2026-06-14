from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel


class Playlist(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True, default="")
    hero_image_url = models.URLField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "funds_playlist"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
