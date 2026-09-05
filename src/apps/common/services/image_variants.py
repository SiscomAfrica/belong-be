from __future__ import annotations

import io
import os
from typing import Final

from PIL import Image, ImageOps

# The widths the app actually renders, in device pixels for a 3x screen.
# Named for the surface so the client and the generator cannot drift: the
# mobile IMAGE_WIDTH table must hold these same numbers.
VARIANT_WIDTHS: Final[dict[str, int]] = {
    "logo": 120,  # HoldingLogo, 40dp
    "thumb": 160,  # list rows, 40-48dp
    "card": 560,  # TrendingJamCard, 180dp
    "hero": 1200,  # FundDetailHero, full bleed
}

WEBP_QUALITY: Final = 82



def variant_key(*, original_key: str, width: int) -> str:
    """Deterministic key for a resized copy.

    Derived from the original rather than recorded, so the client can build the
    URL it wants without the API having to enumerate what exists.
    """
    root, _ = os.path.splitext(original_key)
    return f"{root}__{width}.webp"


def variant_keys(*, original_key: str) -> dict[str, str]:
    return {
        name: variant_key(original_key=original_key, width=width)
        for name, width in VARIANT_WIDTHS.items()
    }


def resize_to_webp(*, image_bytes: bytes, width: int) -> bytes:
    """Downscale to `width` and encode as WebP.

    Never upscales: a source narrower than the target is encoded as-is, so a
    small logo does not get blown up into a larger file than the original.
    """
    with Image.open(io.BytesIO(image_bytes)) as img:
        # Decode large JPEGs at a reduced scale instead of at full size. The
        # catalogue holds sources up to 6067x3467 (~21 megapixels, ~84MB once
        # expanded to RGBA) and the worker runs two at a time inside a 384MB
        # container. draft() lets the decoder do the first 1/2, 1/4 or 1/8 of
        # the downscale, so a thumbnail never materialises the full bitmap.
        # It is a no-op for formats that do not support it.
        img.draft("RGB", (width, width))

        # Phone cameras and design exports carry EXIF rotation. Without this
        # the resized copy is silently rotated relative to the original.
        img = ImageOps.exif_transpose(img)
        img = img.convert("RGBA" if img.mode in ("RGBA", "P", "LA") else "RGB")

        if img.width > width:
            height = round(img.height * width / img.width)
            img = img.resize((width, height), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=WEBP_QUALITY, method=6)
        return buf.getvalue()
