# Generated by Django 4.1.13 on 2024-02-06 23:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ej_tools", "0002_opinioncomponent"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="opinioncomponent",
            name="background_image",
        ),
    ]