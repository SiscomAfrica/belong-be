from __future__ import annotations

from django.apps import AppConfig


class PoolsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.pools"
    verbose_name = "Pools"
