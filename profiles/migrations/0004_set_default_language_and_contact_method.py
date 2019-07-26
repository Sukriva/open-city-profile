# Generated by Django 2.0.5 on 2018-09-18 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("profiles", "0003_add_division_of_interest_model")]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="contact_method",
            field=models.CharField(
                choices=[("email", "Email"), ("sms", "SMS")],
                default="email",
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="language",
            field=models.CharField(
                choices=[("fi", "Finnish"), ("en", "English"), ("sv", "Swedish")],
                default="fi",
                max_length=7,
            ),
        ),
    ]
