from __future__ import annotations

import io

import pytest
from PIL import Image

from apps.common.services.source_image import MAX_SOURCE_WIDTH, cap_source_image


def encoded(*, width: int, height: int, fmt: str = "JPEG", mode: str = "RGB") -> bytes:
    buf = io.BytesIO()
    Image.new(mode, (width, height), (30, 120, 200)).save(buf, format=fmt)
    return buf.getvalue()


def test_oversized_source_is_capped_to_the_maximum_width() -> None:
    """The catalogue held a 6067px source behind a 40dp thumbnail."""
    out = cap_source_image(image_bytes=encoded(width=6067, height=3467))

    assert out is not None
    assert Image.open(io.BytesIO(out)).width == MAX_SOURCE_WIDTH


def test_capping_preserves_aspect_ratio() -> None:
    out = cap_source_image(image_bytes=encoded(width=6000, height=3000))

    image = Image.open(io.BytesIO(out))
    assert image.height == MAX_SOURCE_WIDTH // 2


def test_a_source_within_the_cap_is_left_alone() -> None:
    """Returning None is what makes re-running the backfill free."""
    assert cap_source_image(image_bytes=encoded(width=1200, height=800)) is None
    assert cap_source_image(image_bytes=encoded(width=MAX_SOURCE_WIDTH, height=10)) is None


@pytest.mark.parametrize("fmt", ["JPEG", "PNG", "WEBP"])
def test_format_is_preserved(fmt: str) -> None:
    """A PNG that came back as JPEG would lose transparency silently."""
    out = cap_source_image(image_bytes=encoded(width=4000, height=2000, fmt=fmt))

    assert Image.open(io.BytesIO(out)).format == fmt


def test_transparency_survives_capping() -> None:
    source = encoded(width=4000, height=2000, fmt="PNG", mode="RGBA")

    out = cap_source_image(image_bytes=source)

    assert Image.open(io.BytesIO(out)).mode in ("RGBA", "LA", "P")


def test_capping_actually_saves_bytes() -> None:
    source = encoded(width=6000, height=4000)

    out = cap_source_image(image_bytes=source)

    assert len(out) < len(source)
