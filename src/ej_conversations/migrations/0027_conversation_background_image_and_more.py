# Generated by Django 4.1.13 on 2024-02-07 01:47

from django.db import migrations, models
from ej_conversations.validators import validate_file_size


class Migration(migrations.Migration):

    dependencies = [
        ("ej_conversations", "0026_alter_vote_channel"),
    ]

    operations = [
        migrations.AddField(
            model_name="conversation",
            name="background_image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="conversations/background/",
                validators=[validate_file_size],
                verbose_name="Background image",
            ),
        ),
        migrations.AlterField(
            model_name="conversation",
            name="text",
            field=models.TextField(
                help_text="What do you want to know from participants? The question is the central part of the conversation, from there you can create more specific comments.",
                verbose_name="Question",
            ),
        ),
    ]
