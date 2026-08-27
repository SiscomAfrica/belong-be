from __future__ import annotations

import io
import os

from PIL import Image


def to_webp(
    *,
    image_bytes: bytes,
    quality: int = 80,
) -> bytes:
    """Convert image bytes to WebP format."""
    with Image.open(io.BytesIO(image_bytes)) as img:
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGBA")
        else:
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=quality)
        return buf.getvalue()


def webp_key_for(*, original_key: str) -> str:
    """Return the .webp variant of a storage key."""
    root, _ = os.path.splitext(original_key)
    return f"{root}.webp"
