from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.common.tasks import generate_image_variants
from apps.funds.models import Fund, Playlist


@receiver(post_save, sender=Fund)
@receiver(post_save, sender=Playlist)
def sync_hero_image_url(sender, instance, **kwargs) -> None:  # noqa: ANN001, ANN003
    if instance.hero_image:
        file_key = instance.hero_image.name
        if instance.hero_image_url != file_key:
            sender.objects.filter(pk=instance.pk).update(
                hero_image_url=file_key,
            )
            generate_image_variants.delay(
                file_key,
                instance._meta.label,
                str(instance.pk),
            )
