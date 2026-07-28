from __future__ import annotations

from django.utils.html import format_html


class HeroImageAdminMixin:
    def hero_image_preview(self, obj) -> str:  # noqa: ANN001
        url = ""
        if obj.hero_image:
            url = obj.hero_image.url
        elif obj.hero_image_url:
            url = obj.hero_image_url
        if url:
            return format_html(
                '<img src="{}" style="max-height:80px;max-width:120px;" />',
                url,
            )
        return "-"

    hero_image_preview.short_description = "Preview"  # type: ignore[attr-defined]
