from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import override_settings

from open_city_profile.exceptions import ProfileMustHaveOnePrimaryEmail
from services.enums import ServiceType

from ..models import Email, Profile, TemporaryReadAccessToken
from ..schema import validate_primary_email
from .factories import (
    EmailFactory,
    ProfileWithPrimaryEmailFactory,
    SensitiveDataFactory,
    VerifiedPersonalInformationFactory,
)

User = get_user_model()

GDPR_URL = "https://example.com/"


def test_new_profile_with_default_name(user):
    profile = Profile.objects.create(user=user)
    assert profile.first_name == user.first_name
    assert profile.last_name == user.last_name


def test_new_profile_without_default_name():
    user = User.objects.create(email="test@user.com", username="user")
    profile = Profile.objects.create(user=user)
    assert profile.first_name == ""
    assert profile.last_name == ""


def test_new_profile_with_existing_name_and_default_name(user):
    profile = Profile.objects.create(
        first_name="Existingfirstname", last_name="Existinglastname", user=user
    )
    assert profile.first_name == "Existingfirstname"
    assert profile.last_name == "Existinglastname"


def test_new_profile_with_non_existing_name_and_default_name(user):
    profile = Profile.objects.create(first_name="", last_name="", user=user)
    assert profile.first_name
    assert profile.last_name


def test_serialize_profile(profile):
    email_2 = EmailFactory(profile=profile)
    email_1 = EmailFactory(profile=profile)
    sensitive_data = SensitiveDataFactory(profile=profile)
    serialized_profile = profile.serialize()
    expected_firstname = {"key": "FIRST_NAME", "value": profile.first_name}
    expected_email = {
        "key": "EMAILS",
        "children": [
            {
                "key": "EMAIL",
                "children": [
                    {"key": "PRIMARY", "value": email_1.primary},
                    {"key": "EMAIL_TYPE", "value": email_1.email_type.name},
                    {"key": "EMAIL", "value": email_1.email},
                ],
            },
            {
                "key": "EMAIL",
                "children": [
                    {"key": "PRIMARY", "value": email_2.primary},
                    {"key": "EMAIL_TYPE", "value": email_2.email_type.name},
                    {"key": "EMAIL", "value": email_2.email},
                ],
            },
        ],
    }
    expected_sensitive_data = {
        "key": "SENSITIVEDATA",
        "children": [{"key": "SSN", "value": sensitive_data.ssn}],
    }
    assert "key" in serialized_profile
    assert "children" in serialized_profile
    assert serialized_profile.get("key") == "PROFILE"
    assert expected_firstname in serialized_profile.get("children")
    assert expected_email in serialized_profile.get("children")
    assert expected_sensitive_data in serialized_profile.get("children")


def test_import_customer_data_with_valid_data_set(service_factory):
    service_factory()
    data = [
        {
            "customer_id": "321456",
            "first_name": "Jukka",
            "last_name": "Virtanen",
            "ssn": "010190-001A",
            "email": "jukka.virtanen@example.com",
            "address": {
                "address": "Mannerheimintie 1 A 11",
                "postal_code": "00100",
                "city": "Helsinki",
            },
            "phones": ["0412345678", "358 503334411", "755 1122 K"],
        },
        {
            "customer_id": "321457",
            "first_name": "",
            "last_name": "",
            "ssn": "101086-1234",
            "email": "mirja.korhonen@example.com",
            "address": None,
            "phones": [],
        },
    ]
    assert Profile.objects.count() == 0
    result = Profile.import_customer_data(data)
    assert len(result.keys()) == 2
    profiles = Profile.objects.all()
    assert len(profiles) == 2
    for profile in profiles:
        assert (
            profile.service_connections.first().service.service_type
            == ServiceType.BERTH
        )


def test_import_customer_data_with_missing_customer_id():
    data = [
        {
            "first_name": "Jukka",
            "last_name": "Virtanen",
            "ssn": "010190-001A",
            "email": "jukka.virtanen@example.com",
            "address": {
                "address": "Mannerheimintie 1 A 11",
                "postal_code": "00100",
                "city": "Helsinki",
            },
            "phones": ["0412345678", "358 503334411", "755 1122 K"],
        },
        {
            "customer_id": "321457",
            "first_name": "",
            "last_name": "",
            "ssn": "101086-1234",
            "email": "mirja.korhonen@example.com",
            "address": None,
            "phones": [],
        },
    ]
    assert Profile.objects.count() == 0
    with pytest.raises(Exception) as e:
        Profile.import_customer_data(data)
    assert str(e.value) == "Could not import unknown customer, index: 0"
    assert Profile.objects.count() == 0


def test_import_customer_data_with_missing_email():
    data = [
        {
            "customer_id": "321457",
            "first_name": "Jukka",
            "last_name": "Virtanen",
            "ssn": "010190-001A",
            "address": {
                "address": "Mannerheimintie 1 A 11",
                "postal_code": "00100",
                "city": "Helsinki",
            },
            "phones": ["0412345678", "358 503334411", "755 1122 K"],
        }
    ]
    assert Profile.objects.count() == 0
    with pytest.raises(ProfileMustHaveOnePrimaryEmail) as e:
        Profile.import_customer_data(data)
    assert str(e.value) == "Profile must have exactly one primary email, index: 0"
    assert Profile.objects.count() == 0


def test_validation_should_pass_with_one_primary_email():
    profile = ProfileWithPrimaryEmailFactory()
    validate_primary_email(profile)


def test_validation_should_fail_with_no_primary_email(profile):
    with pytest.raises(ProfileMustHaveOnePrimaryEmail):
        validate_primary_email(profile)


def test_validation_should_fail_with_multiple_primary_emails(profile):
    EmailFactory(profile=profile, primary=True)
    EmailFactory(profile=profile, primary=True)
    with pytest.raises(ProfileMustHaveOnePrimaryEmail):
        validate_primary_email(profile)


def test_validation_should_fail_with_invalid_email():
    e = Email("!dsdsd{}{}{}{}{}{")
    with pytest.raises(ValidationError):
        e.save()


class ValidationTestBase:
    @staticmethod
    def passes_validation(instance):
        try:
            instance.save()
        except ValidationError as err:
            assert err is None

    @staticmethod
    def fails_validation(instance):
        with pytest.raises(ValidationError):
            instance.save()

    @staticmethod
    def execute_string_field_max_length_validation_test(
        instance, field_name, max_length
    ):
        setattr(instance, field_name, "x" * max_length)
        ValidationTestBase.passes_validation(instance)

        setattr(instance, field_name, "x" * (max_length + 1))
        ValidationTestBase.fails_validation(instance)


class TestVerifiedPersonalInformationValidation(ValidationTestBase):
    @pytest.mark.parametrize(
        "field_name,max_length",
        [
            ("first_name", 1024),
            ("last_name", 1024),
            ("given_name", 1024),
            ("national_identification_number", 1024),
            ("email", 1024),
            ("municipality_of_residence", 1024),
            ("municipality_of_residence_number", 4),
        ],
    )
    def test_string_field_max_length(self, field_name, max_length):
        info = VerifiedPersonalInformationFactory()

        self.execute_string_field_max_length_validation_test(
            info, field_name, max_length
        )


@pytest.mark.parametrize("address_type", ["permanent_address", "temporary_address"])
class TestVerifiedPersonalInformationAddressValidation(ValidationTestBase):
    @pytest.mark.parametrize(
        "field_name,max_length",
        [("street_address", 1024), ("postal_code", 1024), ("post_office", 1024)],
    )
    def test_string_field_max_length(self, address_type, field_name, max_length):
        address = getattr(VerifiedPersonalInformationFactory(), address_type)

        self.execute_string_field_max_length_validation_test(
            address, field_name, max_length
        )


class TestVerifiedPersonalInformationPermanentForeignAddressValidation(
    ValidationTestBase
):
    @pytest.mark.parametrize(
        "field_name,max_length",
        [("street_address", 1024), ("additional_address", 1024), ("country_code", 3)],
    )
    def test_string_field_max_length(self, field_name, max_length):
        address = VerifiedPersonalInformationFactory().permanent_foreign_address

        self.execute_string_field_max_length_validation_test(
            address, field_name, max_length
        )


class TestTemporaryReadAccessTokenValidityDuration:
    def test_by_default_validity_duration_is_two_days(self):
        token = TemporaryReadAccessToken()
        assert token.validity_duration == timedelta(days=2)

    @override_settings(TEMPORARY_PROFILE_READ_ACCESS_TOKEN_VALIDITY_MINUTES=60)
    def test_validity_duration_can_be_controlled_with_a_setting(self):
        token = TemporaryReadAccessToken()
        assert token.validity_duration == timedelta(minutes=60)
