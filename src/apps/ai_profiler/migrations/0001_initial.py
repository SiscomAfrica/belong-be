# Generated manually

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("funds", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConversationSession",
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
                    "status",
                    models.CharField(
                        choices=[
                            ("ACTIVE", "Active"),
                            ("COMPLETED", "Completed"),
                            ("ABANDONED", "Abandoned"),
                        ],
                        db_index=True,
                        default="ACTIVE",
                        max_length=20,
                    ),
                ),
                ("summary", models.TextField(blank=True, default="")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ai_sessions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "ai_profiler_session",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ConversationMessage",
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
                    "role",
                    models.CharField(
                        choices=[
                            ("SYSTEM", "System"),
                            ("USER", "User"),
                            ("ASSISTANT", "Assistant"),
                        ],
                        max_length=10,
                    ),
                ),
                ("content", models.TextField()),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="messages",
                        to="ai_profiler.conversationsession",
                    ),
                ),
            ],
            options={
                "db_table": "ai_profiler_message",
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="InvestorProfile",
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
                    "risk_tolerance",
                    models.IntegerField(
                        help_text="1 (very low) to 5 (very high)",
                    ),
                ),
                (
                    "time_horizon",
                    models.CharField(
                        choices=[
                            ("SHORT", "Short Term"),
                            ("MEDIUM", "Medium Term"),
                            ("LONG", "Long Term"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "investment_goal",
                    models.TextField(blank=True, default=""),
                ),
                ("interests", models.JSONField(default=list)),
                (
                    "recommended_fund",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="funds.fund",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="investor_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "ai_profiler_investor_profile",
            },
        ),
    ]
