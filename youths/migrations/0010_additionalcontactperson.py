# Generated by Django 2.2.10 on 2020-06-23 08:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("youths", "0009_youthprofile_membership_number"),
    ]

    operations = [
        migrations.CreateModel(
            name="AdditionalContactPerson",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("phone", models.CharField(max_length=50)),
                ("email", models.EmailField(max_length=254)),
                (
                    "youth_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="additional_contact_persons",
                        to="youths.YouthProfile",
                    ),
                ),
            ],
            options={"abstract": False,},
        ),
    ]
