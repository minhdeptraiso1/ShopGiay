import pytest
from django.contrib.auth import get_user_model

from apps.accounts.roles import BusinessRole

User = get_user_model()


def csrf_header(client) -> dict[str, str]:
    response = client.get("/api/v1/auth/csrf/")
    return {"HTTP_X_CSRFTOKEN": response.data["csrf_token"]}


def registration_payload(**overrides):
    payload = {
        "email": "new-customer@example.com",
        "full_name": "New Customer",
        "password": "StrongPass!123",
        "password_confirm": "StrongPass!123",
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_registration_creates_customer_without_privilege_escalation(csrf_client):
    payload = registration_payload(is_staff=True, is_superuser=True, roles=["ADMIN"])
    response = csrf_client.post(
        "/api/v1/auth/register/", payload, format="json", **csrf_header(csrf_client)
    )

    assert response.status_code == 201
    user = User.objects.get(email="new-customer@example.com")
    assert user.check_password("StrongPass!123")
    assert user.is_staff is False
    assert user.is_superuser is False
    assert response.data["user"]["roles"] == [BusinessRole.CUSTOMER]
    assert response.data["user"]["permissions"] == []


@pytest.mark.django_db
def test_registration_rejects_duplicate_email_case_insensitively(csrf_client):
    User.objects.create_user(email="person@example.com", password="StrongPass!123")
    response = csrf_client.post(
        "/api/v1/auth/register/",
        registration_payload(email="PERSON@example.com"),
        format="json",
        **csrf_header(csrf_client),
    )

    assert response.status_code == 400
    assert "email" in response.data["details"]


@pytest.mark.django_db
def test_registration_requires_csrf_and_matching_strong_password(csrf_client):
    missing_csrf = csrf_client.post("/api/v1/auth/register/", registration_payload(), format="json")
    assert missing_csrf.status_code == 403

    weak_password = csrf_client.post(
        "/api/v1/auth/register/",
        registration_payload(password="123456", password_confirm="different"),
        format="json",
        **csrf_header(csrf_client),
    )
    assert weak_password.status_code == 400
    assert "password_confirm" in weak_password.data["details"]
