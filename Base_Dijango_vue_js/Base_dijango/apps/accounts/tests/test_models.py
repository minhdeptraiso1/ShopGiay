import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import override_settings

User = get_user_model()


@pytest.mark.django_db
def test_create_user_normalizes_email_and_hashes_password():
    user = User.objects.create_user("  Test@Example.COM ", "StrongPass!123")
    assert user.email == "test@example.com"
    assert user.check_password("StrongPass!123")
    assert user.password != "StrongPass!123"


@pytest.mark.django_db
def test_create_superuser_sets_required_flags():
    user = User.objects.create_superuser("admin@example.com", "StrongPass!123")
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.is_active is True


@pytest.mark.django_db(transaction=True)
def test_email_is_unique_case_insensitively():
    User.objects.create_user("same@example.com", "StrongPass!123")
    with pytest.raises(IntegrityError), transaction.atomic():
        duplicate = User(email="SAME@example.com")
        duplicate.set_password("StrongPass!123")
        duplicate.save()


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_seed_dev_user_creates_login_ready_account():
    call_command(
        "seed_dev_user",
        email="demo@example.com",
        password="123456",
        verbosity=0,
    )
    user = User.objects.get(email="demo@example.com")
    assert user.password != "123456"
    assert identify_hasher(user.password) is not None
    assert user.check_password("123456")
    assert user.is_active is True
    assert user.is_staff is False
    assert user.is_superuser is False
