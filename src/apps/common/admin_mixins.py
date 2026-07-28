from __future__ import annotations

from django.utils.html import format_html

from apps.common.services.s3 import generate_presigned_download


class HeroImageAdminMixin:
    def hero_image_preview(self, obj) -> str:  # noqa: ANN001
        if obj.hero_image:
            url = obj.hero_image.url
        elif obj.hero_image_url:
            key = obj.hero_image_url
            if key.startswith("http"):
                url = key
            else:
                url = generate_presigned_download(file_key=key)["download_url"]
        else:
            return "-"
        return format_html(
            '<img src="{}" style="max-height:80px;max-width:120px;" />',
            url,
        )

    hero_image_preview.short_description = "Preview"  # type: ignore[attr-defined]
