from __future__ import annotations

import os


def hero_image_upload_path(instance, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    model_label = instance._meta.model_name
    return f"hero_images/{model_label}s/{instance.pk}{ext}"
