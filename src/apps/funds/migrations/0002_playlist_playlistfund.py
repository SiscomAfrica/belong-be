# Generated manually

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("funds", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="fund",
            name="emoji",
            field=models.CharField(blank=True, default="", max_length=10),
        ),
        migrations.CreateModel(
            name="Playlist",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(unique=True)),
                ("description", models.TextField(blank=True, default="")),
                ("hero_image_url", models.URLField(blank=True, default="")),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "funds_playlist",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="PlaylistFund",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("position", models.PositiveIntegerField(default=0)),
                (
                    "returns_label",
                    models.CharField(
                        blank=True,
                        default="Annualised returns",
                        max_length=100,
                    ),
                ),
                (
                    "fund",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="playlist_entries",
                        to="funds.fund",
                    ),
                ),
                (
                    "playlist",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="playlist_funds",
                        to="funds.playlist",
                    ),
                ),
            ],
            options={
                "db_table": "funds_playlist_fund",
                "ordering": ["position"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("playlist", "fund"),
                        name="unique_playlist_fund",
                    ),
                ],
            },
        ),
    ]
