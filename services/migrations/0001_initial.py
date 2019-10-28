# Generated by Django 2.2.3 on 2019-10-28 12:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [("profiles", "0008_add_first_name_and_last_name_to_profile")]

    operations = [
        migrations.CreateModel(
            name="Service",
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
                (
                    "service_type",
                    models.CharField(
                        choices=[
                            ("HKI_MY_DATA", "HKI_MY_DATA"),
                            ("BERTH", "BERTH"),
                            ("YOUTH_MEMBERSHIP", "YOUTH_MEMBERSHIP"),
                            ("GODCHILDREN_OF_CULTURE", "GODCHILDREN_OF_CULTURE"),
                        ],
                        max_length=32,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="profiles.Profile",
                    ),
                ),
            ],
        )
    ]
