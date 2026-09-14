import pytest

from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_profile_update_only_accepts_full_name(api_client):
    user = UserFactory(is_staff=False, is_superuser=False)
    api_client.force_authenticate(user)
    response = api_client.patch(
        "/api/v1/auth/me/",
        {
            "full_name": "New Name",
            "email": "attacker@example.com",
            "is_staff": True,
            "is_superuser": True,
            "groups": [1],
        },
        format="json",
    )
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.full_name == "New Name"
    assert user.email != "attacker@example.com"
    assert user.is_staff is False
    assert user.is_superuser is False
