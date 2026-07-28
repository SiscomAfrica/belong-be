from __future__ import annotations

from django.db import models

from apps.common.models.base import BaseModel
from apps.common.storage import hero_image_upload_path
from apps.common.validators import validate_image_max_5mb


class Playlist(BaseModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True, default="")
    hero_image_url = models.URLField(blank=True, default="")
    hero_image = models.ImageField(
        upload_to=hero_image_upload_path,
        blank=True,
        default="",
        validators=[validate_image_max_5mb],
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "funds_playlist"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name
