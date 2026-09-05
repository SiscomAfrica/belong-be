from __future__ import annotations

import logging

from celery import shared_task

from apps.common.services.image_variants import VARIANT_WIDTHS, resize_to_webp, variant_key
from apps.common.services.s3_objects import (
    catalogue_storage,
    download_bytes,
    upload_bytes,
)

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="apps.common.tasks.generate_image_variants",
    max_retries=3,
    default_retry_delay=30,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_jitter=True,
    task_time_limit=300,
    task_soft_time_limit=240,
)
def generate_image_variants(
    self,
    original_key: str,
    model_label: str = "",
    pk: str = "",
) -> list[str]:
    """Pre-render every size the app renders, once, at upload time.

    The app asks for a specific width by key, so these have to exist before the
    URL is handed out. Idempotent: re-running overwrites in place, which is
    what makes both the Celery retry and the backfill command safe.
    """
    if "__" in original_key.rsplit("/", 1)[-1]:
        # Already a generated variant. Guards against a signal firing on a save
        # that was itself triggered by this task.
        return []

    # Catalogue art lives in the public bucket, not the default (private) one,
    # so both ends of the round trip have to be pointed at it.
    storage = catalogue_storage()
    source = download_bytes(key=original_key, storage=storage)

    written: list[str] = []
    for name, width in VARIANT_WIDTHS.items():
        key = variant_key(original_key=original_key, width=width)
        upload_bytes(
            key=key,
            data=resize_to_webp(image_bytes=source, width=width),
            content_type="image/webp",
            storage=storage,
        )
        written.append(key)
        logger.info(
            "Wrote image variant",
            extra={"model": model_label, "pk": pk, "variant": name, "key": key},
        )

    return written
