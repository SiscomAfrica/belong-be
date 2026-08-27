from __future__ import annotations

import logging

from celery import shared_task

from apps.common.services.image_convert import to_webp, webp_key_for
from apps.common.services.s3_objects import download_bytes, upload_bytes

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    name="apps.common.tasks.convert_image_to_webp",
    max_retries=3,
    default_retry_delay=30,
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_jitter=True,
    task_time_limit=120,
    task_soft_time_limit=90,
)
def convert_image_to_webp(
    self,  # noqa: ANN001
    original_key: str,
    model_label: str,
    pk: str,
) -> None:
    """Download an image from S3, convert to WebP, upload."""
    if original_key.endswith(".webp"):
        return

    log = logger.bind(task_id=self.request.id) if hasattr(logger, "bind") else logger
    log.info(
        "Converting image to WebP",
        extra={"model": model_label, "pk": pk, "key": original_key},
    )

    image_bytes = download_bytes(key=original_key)
    webp_bytes = to_webp(image_bytes=image_bytes)
    webp_key = webp_key_for(original_key=original_key)

    upload_bytes(
        key=webp_key,
        data=webp_bytes,
        content_type="image/webp",
    )

    log.info(
        "WebP conversion complete",
        extra={"model": model_label, "pk": pk, "webp_key": webp_key},
    )
