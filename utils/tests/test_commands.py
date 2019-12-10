from django.contrib.auth.models import Group
from django.core.management import call_command

from profiles.models import Profile
from services.enums import ServiceType
from services.models import Service
from users.models import User
from youths.models import YouthProfile


def test_command_seed_data_works_without_arguments():
    call_command("seed_data")
    assert Service.objects.count() == len(ServiceType)
    assert Group.objects.count() == len(ServiceType)
    anonymous_users = 1
    admin_users = 1
    normal_users = 50
    assert (
        User.objects.count()
        == normal_users + len(ServiceType) + admin_users + anonymous_users
    )
    assert Profile.objects.count() == normal_users
    assert YouthProfile.objects.count() == 10
    assert User.objects.filter(is_superuser=True).count() == 1


def test_command_seed_data_works_withs_arguments():
    args = [
        "--profilecount=20",
        "--youthprofilepercentage=0.5",
        "--locale=fi_FI",
        "--nosuperuser",
    ]
    call_command("seed_data", *args)
    assert Profile.objects.count() == 20
    assert YouthProfile.objects.count() == 10
    assert User.objects.filter(is_superuser=True).count() == 0