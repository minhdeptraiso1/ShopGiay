import pytest

from apps.accounts.services import update_profile
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_update_profile_trims_name_and_preserves_permissions():
    user = UserFactory(is_staff=False)
    updated = update_profile(user=user, full_name="  Nguyễn Văn A  ")
    assert updated.full_name == "Nguyễn Văn A"
    assert updated.is_staff is False
