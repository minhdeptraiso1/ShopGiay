from urllib.parse import parse_qs, urlparse

import pytest
from django.contrib.auth import get_user_model
from django.core import mail

from apps.accounts.tests.factories import UserFactory

User = get_user_model()


def csrf_header(client) -> dict[str, str]:
    response = client.get("/api/v1/auth/csrf/")
    return {"HTTP_X_CSRFTOKEN": response.data["csrf_token"]}


@pytest.mark.django_db
def test_password_reset_is_neutral_and_sends_valid_single_use_link(csrf_client):
    user = UserFactory(email="reset@example.com")
    response = csrf_client.post(
        "/api/v1/auth/password-reset/",
        {"email": user.email},
        format="json",
        **csrf_header(csrf_client),
    )
    unknown = csrf_client.post(
        "/api/v1/auth/password-reset/",
        {"email": "unknown@example.com"},
        format="json",
        **csrf_header(csrf_client),
    )

    assert response.status_code == unknown.status_code == 202
    assert response.data == unknown.data
    assert len(mail.outbox) == 1

    reset_url = next(part for part in mail.outbox[0].body.split() if part.startswith("http"))
    query = parse_qs(urlparse(reset_url).query)
    payload = {
        "uid": query["uid"][0],
        "token": query["token"][0],
        "new_password": "NewStrongPass!456",
        "new_password_confirm": "NewStrongPass!456",
    }
    confirmed = csrf_client.post(
        "/api/v1/auth/password-reset/confirm/",
        payload,
        format="json",
        **csrf_header(csrf_client),
    )
    assert confirmed.status_code == 204
    user.refresh_from_db()
    assert user.check_password("NewStrongPass!456")

    reused = csrf_client.post(
        "/api/v1/auth/password-reset/confirm/",
        payload,
        format="json",
        **csrf_header(csrf_client),
    )
    assert reused.status_code == 400
    assert reused.data["code"] == "invalid_reset_token"


@pytest.mark.django_db
def test_password_reset_rejects_invalid_token_without_changing_password(csrf_client):
    user = UserFactory()
    response = csrf_client.post(
        "/api/v1/auth/password-reset/confirm/",
        {
            "uid": "invalid",
            "token": "invalid",
            "new_password": "NewStrongPass!456",
            "new_password_confirm": "NewStrongPass!456",
        },
        format="json",
        **csrf_header(csrf_client),
    )
    assert response.status_code == 400
    user.refresh_from_db()
    assert user.check_password("StrongPass!123")
