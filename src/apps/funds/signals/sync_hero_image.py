from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.funds.models import Fund, Playlist


@receiver(post_save, sender=Fund)
@receiver(post_save, sender=Playlist)
def sync_hero_image_url(sender, instance, **kwargs) -> None:  # noqa: ANN001, ANN003
    if instance.hero_image and hasattr(instance.hero_image, "url"):
        new_url = instance.hero_image.url
        if instance.hero_image_url != new_url:
            sender.objects.filter(pk=instance.pk).update(
                hero_image_url=new_url,
            )
