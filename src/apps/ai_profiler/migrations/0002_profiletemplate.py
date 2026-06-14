# Generated manually

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai_profiler", "0001_initial"),
        ("funds", "0002_playlist_playlistfund"),
    ]

    operations = [
        migrations.CreateModel(
            name="ProfileTemplate",
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
                (
                    "investor_type",
                    models.CharField(
                        choices=[
                            ("CONSERVATIVE", "Conservative"),
                            ("MODERATE", "Moderate"),
                            ("INTERMEDIATE", "Intermediate"),
                            ("AGGRESSIVE", "Aggressive"),
                            ("HIGH_RISK", "High Risk"),
                        ],
                        max_length=20,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(unique=True)),
                (
                    "accent",
                    models.CharField(default="investor.", max_length=50),
                ),
                ("badge_label", models.CharField(max_length=50)),
                ("description", models.TextField()),
                (
                    "section_title",
                    models.CharField(
                        default="Hand picked jams", max_length=100,
                    ),
                ),
                (
                    "section_action",
                    models.CharField(
                        default="Tap any to Invest", max_length=100,
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("position", models.PositiveIntegerField(default=0)),
                (
                    "playlist",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="profile_templates",
                        to="funds.playlist",
                    ),
                ),
            ],
            options={
                "db_table": "ai_profiler_profile_template",
                "ordering": ["position"],
            },
        ),
    ]
