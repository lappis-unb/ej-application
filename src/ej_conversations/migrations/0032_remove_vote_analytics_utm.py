# Generated by Django 4.1.13 on 2024-05-01 23:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ej_conversations", "0031_alter_vote_channel"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="vote",
            name="analytics_utm",
        ),
    ]
