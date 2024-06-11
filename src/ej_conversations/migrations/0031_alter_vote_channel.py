# Generated by Django 4.1.13 on 2024-05-01 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ej_conversations", "0030_conversation_logo_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="vote",
            name="channel",
            field=models.CharField(
                choices=[
                    ("telegram", "Telegram"),
                    ("whatsapp", "Whatsapp"),
                    ("rasa", "RASAX"),
                    ("opinion_component", "Opinion Component"),
                    ("socketio", "Rasa webchat"),
                    ("ej", "EJ"),
                    ("unknown", "Unknown"),
                ],
                default="unknown",
                help_text="From which EJ channel the vote comes from",
                max_length=50,
                verbose_name="Channel",
            ),
        ),
    ]