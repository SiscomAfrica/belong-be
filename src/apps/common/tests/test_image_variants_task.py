from __future__ import annotations

import io

import pytest
from django.core.files.storage import InMemoryStorage
from PIL import Image

from apps.common.services.image_variants import VARIANT_WIDTHS, variant_key
from apps.common.services.source_image import MAX_SOURCE_WIDTH
from apps.common.tasks import image_variants as task_module
from apps.common.tasks.image_variants import generate_image_variants

PUBLIC_KEY = "hero_images/funds/abc.jpg"
PRIVATE_KEY = "profile-photos/9f/me.jpg"


@pytest.fixture
def storage(monkeypatch) -> InMemoryStorage:
    """Stand in for both buckets so the task can be run for real."""
    store = InMemoryStorage()
    # Patched on the task module, not on s3_objects: the task imported the
    # name directly, so it holds its own reference.
    monkeypatch.setattr(task_module, "storage_for", lambda key: store)
    return store


def seed(store: InMemoryStorage, key: str, *, width: int, height: int) -> None:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), (10, 90, 200)).save(buf, format="JPEG")
    store.save(key, io.BytesIO(buf.getvalue()))


def stored_width(store: InMemoryStorage, key: str) -> int:
    with store.open(key, "rb") as f:
        return Image.open(io.BytesIO(f.read())).width


def test_every_width_is_written_beside_the_original(storage) -> None:
    seed(storage, PUBLIC_KEY, width=1800, height=1000)

    written = generate_image_variants(PUBLIC_KEY)

    assert len(written) == len(VARIANT_WIDTHS)
    for width in VARIANT_WIDTHS.values():
        assert storage.exists(variant_key(original_key=PUBLIC_KEY, width=width))


def test_rerunning_overwrites_rather_than_duplicating(storage) -> None:
    """Both the Celery retry and the backfill command re-run this."""
    seed(storage, PUBLIC_KEY, width=1800, height=1000)

    assert generate_image_variants(PUBLIC_KEY) == generate_image_variants(PUBLIC_KEY)


def test_a_generated_variant_is_never_reprocessed(storage) -> None:
    """Otherwise a save triggered by this task would recurse into its output."""
    assert generate_image_variants(variant_key(original_key=PUBLIC_KEY, width=160)) == []


def test_a_source_within_the_cap_is_left_untouched(storage) -> None:
    seed(storage, PUBLIC_KEY, width=1800, height=1000)
    with storage.open(PUBLIC_KEY, "rb") as f:
        before = f.read()

    generate_image_variants(PUBLIC_KEY)

    with storage.open(PUBLIC_KEY, "rb") as f:
        assert f.read() == before


def test_an_oversized_source_is_capped_in_place(storage) -> None:
    """Storing a 6067px master to serve a 40dp thumbnail is pure egress waste."""
    seed(storage, PUBLIC_KEY, width=6067, height=3467)

    generate_image_variants(PUBLIC_KEY)

    assert stored_width(storage, PUBLIC_KEY) == MAX_SOURCE_WIDTH


def test_private_uploads_are_capped_but_get_no_variants(storage) -> None:
    """Nothing requests a variant of a profile photo, so writing them is waste."""
    seed(storage, PRIVATE_KEY, width=4000, height=3000)

    written = generate_image_variants(PRIVATE_KEY)

    assert written == []
    assert stored_width(storage, PRIVATE_KEY) == MAX_SOURCE_WIDTH
