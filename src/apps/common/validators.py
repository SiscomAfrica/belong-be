from __future__ import annotations

from django.core.exceptions import ValidationError


def validate_image_max_5mb(value) -> None:  # noqa: ANN001
    max_size = 5 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError("Image file size must be under 5 MB.")
