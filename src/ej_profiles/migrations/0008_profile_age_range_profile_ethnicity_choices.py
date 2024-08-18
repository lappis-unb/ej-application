# Generated by Django 4.1.13 on 2024-08-18 22:13

import boogie.fields.enum_field
from django.db import migrations
import ej_profiles.enums


class Migration(migrations.Migration):

    dependencies = [
        ("ej_profiles", "0007_profile_region"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="age_range",
            field=boogie.fields.enum_field.EnumField(
                ej_profiles.enums.AgeRange,
                default=ej_profiles.enums.AgeRange["NOT_FILLED"],
                verbose_name="Age range",
            ),
        ),
        migrations.AddField(
            model_name="profile",
            name="ethnicity_choices",
            field=boogie.fields.enum_field.EnumField(
                ej_profiles.enums.Ethnicity,
                default=ej_profiles.enums.Ethnicity["NOT_FILLED"],
                verbose_name="Ethnicity",
            ),
        ),
    ]