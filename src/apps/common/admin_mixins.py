from __future__ import annotations

from django.utils.html import format_html

from apps.common.services.media_urls import catalogue_image_field_url


class HeroImageAdminMixin:
    def hero_image_preview(self, obj) -> str:
        url = catalogue_image_field_url(
            image=getattr(obj, "hero_image", None),
            fallback_key=getattr(obj, "hero_image_url", ""),
        )
        if not url:
            return "-"
        return format_html(
            '<img src="{}" style="max-height:80px;max-width:120px;" />',
            url,
        )

    hero_image_preview.short_description = "Preview"  # type: ignore[attr-defined]
