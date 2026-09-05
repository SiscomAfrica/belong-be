from __future__ import annotations

import io

import pytest
from django.core.files.storage import InMemoryStorage
from PIL import Image

from apps.common.services.image_variants import VARIANT_WIDTHS, variant_key
from apps.common.tasks import image_variants as task_module
from apps.common.tasks.image_variants import generate_image_variants

ORIGINAL = "hero_images/funds/abc.jpg"


@pytest.fixture
def storage(monkeypatch) -> InMemoryStorage:
    """Stand in for the public bucket so the task can be run for real."""
    store = InMemoryStorage()
    # Patched on the task module, not on s3_objects: the task imported the
    # name directly, so it holds its own reference.
    monkeypatch.setattr(task_module, "catalogue_storage", lambda: store)
    return store


def seed(store: InMemoryStorage, key: str, *, width: int, height: int) -> None:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), (10, 90, 200)).save(buf, format="JPEG")
    store.save(key, io.BytesIO(buf.getvalue()))


def test_every_width_is_written_beside_the_original(storage) -> None:
    seed(storage, ORIGINAL, width=1800, height=1000)

    written = generate_image_variants(ORIGINAL)

    assert len(written) == len(VARIANT_WIDTHS)
    for width in VARIANT_WIDTHS.values():
        key = variant_key(original_key=ORIGINAL, width=width)
        assert storage.exists(key), f"missing variant for width {width}"


def test_rerunning_overwrites_rather_than_duplicating(storage) -> None:
    """Both the Celery retry and the backfill command re-run this."""
    seed(storage, ORIGINAL, width=1800, height=1000)

    first = generate_image_variants(ORIGINAL)
    second = generate_image_variants(ORIGINAL)

    assert first == second


def test_a_generated_variant_is_never_reprocessed(storage) -> None:
    """Otherwise a save triggered by this task would recurse into its output."""
    already = variant_key(original_key=ORIGINAL, width=160)

    assert generate_image_variants(already) == []


def test_the_original_is_left_untouched(storage) -> None:
    seed(storage, ORIGINAL, width=1800, height=1000)
    before = storage.open(ORIGINAL, "rb").read()

    generate_image_variants(ORIGINAL)

    assert storage.open(ORIGINAL, "rb").read() == before
