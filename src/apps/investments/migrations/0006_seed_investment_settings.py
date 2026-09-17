from __future__ import annotations

from django.db import migrations

# Seeded so the row is there to edit the first time somebody opens the admin,
# rather than appearing only after the first plan is created.
#
# gen_random_uuid() is built into PostgreSQL 13+, which this project pins.
FORWARD_SQL = """
    INSERT INTO investments_settings (id, min_contribution, created_at, updated_at)
    SELECT gen_random_uuid(), 100.00, NOW(), NOW()
    WHERE NOT EXISTS (SELECT 1 FROM investments_settings);
"""

REVERSE_SQL = """
    DELETE FROM investments_settings;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("investments", "0005_investmentsettings"),
    ]

    operations = [
        migrations.RunSQL(sql=FORWARD_SQL, reverse_sql=REVERSE_SQL),
    ]
