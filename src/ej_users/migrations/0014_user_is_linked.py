# Generated by Django 4.1.13 on 2024-07-09 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ej_users", "0013_user_secret_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_linked",
            field=models.BooleanField(default=False),
        ),
    ]