from __future__ import annotations

import io
from typing import Final

from PIL import Image, ImageOps

# Nothing renders wider than the largest variant, so storing more than this is
# bytes nobody will ever fetch. The catalogue held a 6067x3467 source (3.7MB)
# behind a 40dp thumbnail; capped, the same image is a fraction of that in R2
# and in egress. Kept comfortably above `hero` so a future larger surface does
# not need a re-upload.
MAX_SOURCE_WIDTH: Final = 2048

# Re-encode quality for a capped source. Higher than the variants because this
# is the master every variant is derived from.
SOURCE_QUALITY: Final = 88


def cap_source_image(*, image_bytes: bytes) -> bytes | None:
    """Shrink an oversized upload to MAX_SOURCE_WIDTH, keeping its format.

    Returns None when the source is already within the cap, so the caller can
    skip a pointless re-upload — and so re-running over a capped catalogue is
    free rather than re-encoding everything every time.
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        if img.width <= MAX_SOURCE_WIDTH:
            return None

        image_format = (img.format or "JPEG").upper()
        img.draft("RGB", (MAX_SOURCE_WIDTH, MAX_SOURCE_WIDTH))
        img = ImageOps.exif_transpose(img)

        height = round(img.height * MAX_SOURCE_WIDTH / img.width)
        img = img.resize((MAX_SOURCE_WIDTH, height), Image.LANCZOS)

        # JPEG cannot hold an alpha channel; PNG and WebP keep theirs.
        if image_format == "JPEG":
            img = img.convert("RGB")

        buf = io.BytesIO()
        img.save(buf, format=image_format, quality=SOURCE_QUALITY, optimize=True)
        return buf.getvalue()
