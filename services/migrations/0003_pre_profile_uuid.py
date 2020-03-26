# Generated by Django 2.2.4 on 2019-11-05 15:46

from django.db import migrations, models


def match_id_to_uuid(apps, schema_editor):
    Profile = apps.get_model("profiles", "Profile")
    Service = apps.get_model("services", "Service")

    for service in Service.objects.all():
        # reassign profile
        p = Profile.objects.filter(id=service.profile).first()
        if p and p.uuid:
            service.profile = p.uuid
            service.save(update_fields=["profile"])
        else:
            # this should not be the case, but let's ensure
            # that this scenario is handled somewhat gracefully:
            # delete the row, because keeping old values
            # will break the followng migrations
            # (both for migrating backwards and forward)
            service.delete()


def match_uuid_to_id(apps, schema_editor):
    Profile = apps.get_model("profiles", "Profile")
    Service = apps.get_model("services", "Service")

    for service in Service.objects.all():
        # reassign profile
        p = Profile.objects.filter(uuid=service.profile).first()
        if p and p.id:
            service.profile = p.id
            service.save(update_fields=["profile"])
        else:
            # see above
            service.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0002_services_unique_on_profile"),
        ("profiles", "0009_add_profile_uuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="service", name="profile", field=models.CharField(max_length=36)
        ),
        migrations.RunPython(match_id_to_uuid, match_uuid_to_id),
    ]
