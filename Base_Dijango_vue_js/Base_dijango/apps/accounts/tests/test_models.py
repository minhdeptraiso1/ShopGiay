import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import override_settings

from apps.accounts.roles import BusinessRole

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
    assert user.groups.filter(name=BusinessRole.CUSTOMER).exists()


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_seed_dev_user_repairs_missing_customer_role():
    user = User.objects.create_user("demo@example.com", "123456")
    user.groups.clear()

    call_command("seed_dev_user", email=user.email, password="123456", verbosity=0)

    assert user.groups.filter(name=BusinessRole.CUSTOMER).exists()


@pytest.mark.django_db
@override_settings(DEBUG=True, DEMO_USER_PASSWORD="123456")
def test_seed_dev_accounts_creates_and_repairs_all_local_roles():
    call_command("seed_dev_accounts", verbosity=0)

    expected = {
        "customer@example.com": (BusinessRole.CUSTOMER, False, False),
        "staff@example.com": (BusinessRole.STAFF, True, False),
        "admin@example.com": (BusinessRole.ADMIN, True, True),
    }
    for email, (role, is_staff, is_superuser) in expected.items():
        user = User.objects.get(email=email)
        assert user.check_password("123456")
        assert user.is_active is True
        assert user.is_staff is is_staff
        assert user.is_superuser is is_superuser
        assert list(user.groups.values_list("name", flat=True)) == [role]

    admin = User.objects.get(email="admin@example.com")
    admin.set_password("changed-password")
    admin.is_staff = False
    admin.is_superuser = False
    admin.save()
    admin.groups.clear()

    call_command("seed_dev_accounts", verbosity=0)

    admin.refresh_from_db()
    assert admin.check_password("123456")
    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert list(admin.groups.values_list("name", flat=True)) == [BusinessRole.ADMIN]
