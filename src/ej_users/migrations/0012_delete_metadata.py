# Generated by Django 4.1.13 on 2024-05-21 01:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ej_users", "0011_remove_user_signature"),
    ]

    operations = [
        migrations.DeleteModel(
            name="MetaData",
        ),
    ]
