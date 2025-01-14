# Generated by Django 4.1.13 on 2023-12-27 23:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("taggit", "0003_taggeditem_add_unique_index"),
        ("ej_conversations", "0024_alter_conversation_welcome_message"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversationtag",
            name="tag",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(app_label)s_%(class)s_items",
                to="taggit.tag",
            ),
        ),
    ]
