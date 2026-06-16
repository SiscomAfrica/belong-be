from django.db import migrations

import apps.users.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelManagers(
            name="user",
            managers=[
                ("objects", apps.users.models.manager.UserManager()),
            ],
        ),
    ]
