from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.common.tasks import generate_image_variants
from apps.funds.models import FundHolding


@receiver(post_save, sender=FundHolding)
def sync_holding_logo_url(sender, instance, **kwargs) -> None:  # noqa: ANN001, ANN003
    if instance.logo_image:
        file_key = instance.logo_image.name
        if instance.logo_url != file_key:
            sender.objects.filter(pk=instance.pk).update(
                logo_url=file_key,
            )
            generate_image_variants.delay(
                file_key,
                instance._meta.label,
                str(instance.pk),
            )
