from __future__ import annotations

import io

from PIL import Image

from apps.common.services.image_variants import (
    VARIANT_WIDTHS,
    resize_to_webp,
    variant_key,
    variant_keys,
)


def png_bytes(*, width: int, height: int) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), (120, 20, 100)).save(buf, format="PNG")
    return buf.getvalue()


def decoded(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data))


def test_variant_key_swaps_extension_and_tags_the_width() -> None:
    key = variant_key(original_key="hero_images/funds/abc.jpg", width=160)

    assert key == "hero_images/funds/abc__160.webp"


def test_variant_keys_cover_every_width_the_app_asks_for() -> None:
    keys = variant_keys(original_key="hero_images/funds/abc.jpg")

    assert set(keys) == set(VARIANT_WIDTHS)
    assert len(set(keys.values())) == len(VARIANT_WIDTHS), "widths must not collide"


def test_resize_downscales_and_keeps_aspect_ratio() -> None:
    out = decoded(resize_to_webp(image_bytes=png_bytes(width=2000, height=1000), width=160))

    assert out.format == "WEBP"
    assert out.width == 160
    assert out.height == 80


def test_resize_never_upscales_a_small_source() -> None:
    """Blowing a small logo up would produce a file larger than the original."""
    out = decoded(resize_to_webp(image_bytes=png_bytes(width=64, height=64), width=1200))

    assert out.width == 64


def test_thumbnail_is_dramatically_smaller_than_the_original() -> None:
    """The whole point: a 40dp row must not download a full-size hero."""
    original = png_bytes(width=2000, height=1200)
    thumb = resize_to_webp(image_bytes=original, width=VARIANT_WIDTHS["thumb"])

    assert len(thumb) < len(original) / 10
