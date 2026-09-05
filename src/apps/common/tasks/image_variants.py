from __future__ import annotations

import logging

from celery import shared_task

from apps.common.services.image_variants import (
    VARIANT_WIDTHS,
    resize_to_webp,
    variant_key,
)
from apps.common.services.media_routing import is_public
from apps.common.services.s3_objects import download_bytes, storage_for, upload_bytes
from apps.common.services.source_image import cap_source_image

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
    """Cap an upload to a sane size, then pre-render the sizes the app renders.

    The app asks for a specific width by key, so the variants have to exist
    before the URL is handed out. Idempotent throughout: re-running overwrites
    in place and skips work already done, which is what makes both the Celery
    retry and the backfill command safe to run repeatedly.
    """
    if "__" in original_key.rsplit("/", 1)[-1]:
        # Already a generated variant. Guards against a signal firing on a save
        # that was itself triggered by this task.
        return []

    # Public art and private uploads live in different buckets, addressed by
    # different clients; reading one through the other looks like a 404.
    storage = storage_for(original_key)
    source = download_bytes(key=original_key, storage=storage)

    capped = cap_source_image(image_bytes=source)
    if capped is not None:
        upload_bytes(
            key=original_key,
            data=capped,
            content_type=_content_type_for(original_key),
            storage=storage,
        )
        logger.info(
            "Capped oversized source image",
            extra={
                "model": model_label, "pk": pk, "key": original_key,
                "was_bytes": len(source), "now_bytes": len(capped),
            },
        )
        source = capped

    if not is_public(original_key):
        # Only public art is served by derived variant URL. Generating them for
        # a private upload would write files nothing ever requests.
        return []

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


def _content_type_for(key: str) -> str:
    suffix = key.rsplit(".", 1)[-1].lower()
    return {
        "png": "image/png",
        "webp": "image/webp",
        "gif": "image/gif",
    }.get(suffix, "image/jpeg")
