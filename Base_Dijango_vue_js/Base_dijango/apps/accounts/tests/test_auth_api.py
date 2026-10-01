from datetime import timedelta

import pytest
from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.tests.factories import UserFactory


def csrf_header(client) -> dict[str, str]:
    response = client.get("/api/v1/auth/csrf/")
    assert response.status_code == 200
    assert response["Cache-Control"] == "no-store"
    return {"HTTP_X_CSRFTOKEN": response.data["csrf_token"]}


def login(client, *, email: str, password: str = "StrongPass!123"):
    return client.post(
        "/api/v1/auth/login/",
        {"email": email, "password": password},
        format="json",
        **csrf_header(client),
    )


@pytest.mark.django_db
def test_login_sets_secure_refresh_cookie_contract(csrf_client):
    user = UserFactory(email="person@example.com")
    response = login(csrf_client, email="PERSON@example.com")

    assert response.status_code == 200
    assert response.data["user"]["email"] == user.email
    assert "access" in response.data
    assert "refresh" not in response.data
    assert response["Cache-Control"] == "no-store"

    cookie = response.cookies[settings.REFRESH_TOKEN_COOKIE_NAME]
    assert cookie["httponly"] is True
    assert bool(cookie["secure"]) is settings.REFRESH_TOKEN_COOKIE_SECURE
    assert cookie["samesite"] == "Lax"
    assert cookie["path"] == "/api/v1/auth/"


@pytest.mark.django_db
@pytest.mark.parametrize("endpoint", ["login", "refresh", "logout"])
def test_cookie_auth_endpoints_reject_missing_csrf(csrf_client, endpoint):
    UserFactory(email="person@example.com")
    payload = {"email": "person@example.com", "password": "StrongPass!123"}
    response = csrf_client.post(f"/api/v1/auth/{endpoint}/", payload, format="json")
    assert response.status_code == 403
    assert response.data["code"] == "csrf_failed"


@pytest.mark.django_db
def test_login_rejects_wrong_csrf_token(csrf_client):
    UserFactory(email="person@example.com")
    csrf_header(csrf_client)
    response = csrf_client.post(
        "/api/v1/auth/login/",
        {"email": "person@example.com", "password": "StrongPass!123"},
        format="json",
        HTTP_X_CSRFTOKEN="intentionally-wrong-token",
    )
    assert response.status_code == 403
    assert response.data["code"] == "csrf_failed"


@pytest.mark.django_db
def test_refresh_rotates_cookie_and_blacklists_old_token(csrf_client):
    user = UserFactory()
    login_response = login(csrf_client, email=user.email)
    old_refresh = login_response.cookies[settings.REFRESH_TOKEN_COOKIE_NAME].value

    response = csrf_client.post(
        "/api/v1/auth/refresh/", {}, format="json", **csrf_header(csrf_client)
    )
    assert response.status_code == 200
    assert set(response.data) == {"access"}
    new_refresh = response.cookies[settings.REFRESH_TOKEN_COOKIE_NAME].value
    assert new_refresh != old_refresh

    csrf_client.cookies[settings.REFRESH_TOKEN_COOKIE_NAME] = old_refresh
    rejected = csrf_client.post(
        "/api/v1/auth/refresh/", {}, format="json", **csrf_header(csrf_client)
    )
    assert rejected.status_code == 400
    assert rejected.cookies[settings.REFRESH_TOKEN_COOKIE_NAME]["max-age"] == 0


@pytest.mark.django_db
def test_logout_is_idempotent_without_access_and_revokes_refresh(csrf_client):
    user = UserFactory()
    login_response = login(csrf_client, email=user.email)
    refresh_token = login_response.cookies[settings.REFRESH_TOKEN_COOKIE_NAME].value
    access = login_response.data["access"]

    response = csrf_client.post(
        "/api/v1/auth/logout/", {}, format="json", **csrf_header(csrf_client)
    )
    assert response.status_code == 204
    assert not response.content
    assert response.cookies[settings.REFRESH_TOKEN_COOKIE_NAME]["max-age"] == 0

    csrf_client.cookies[settings.REFRESH_TOKEN_COOKIE_NAME] = refresh_token
    rejected = csrf_client.post(
        "/api/v1/auth/refresh/", {}, format="json", **csrf_header(csrf_client)
    )
    assert rejected.status_code == 400

    csrf_client.cookies.pop(settings.REFRESH_TOKEN_COOKIE_NAME, None)
    repeated = csrf_client.post(
        "/api/v1/auth/logout/", {}, format="json", **csrf_header(csrf_client)
    )
    assert repeated.status_code == 204

    csrf_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    assert csrf_client.get("/api/v1/auth/me/").status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("password", "is_active"),
    [("wrong-password", True), ("StrongPass!123", False)],
)
def test_login_rejects_bad_credentials_without_disclosing_reason(csrf_client, password, is_active):
    UserFactory(email="person@example.com", is_active=is_active)
    response = login(csrf_client, email="person@example.com", password=password)
    assert response.status_code == 401
    assert response.data["code"] == "invalid_credentials"


@pytest.mark.django_db
def test_protected_api_rejects_missing_invalid_and_expired_jwt(api_client):
    user = UserFactory()
    assert api_client.get("/api/v1/auth/me/").status_code == 401

    api_client.credentials(HTTP_AUTHORIZATION="Bearer not-a-jwt")
    assert api_client.get("/api/v1/auth/me/").status_code == 401

    expired = AccessToken.for_user(user)
    expired.set_exp(from_time=timezone.now() - timedelta(minutes=10), lifetime=timedelta(minutes=1))
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {expired}")
    assert api_client.get("/api/v1/auth/me/").status_code == 401


@pytest.mark.django_db
def test_inactive_user_cannot_refresh_or_use_protected_api(csrf_client):
    user = UserFactory()
    login_response = login(csrf_client, email=user.email)
    user.is_active = False
    user.save(update_fields=["is_active"])

    refresh = csrf_client.post(
        "/api/v1/auth/refresh/", {}, format="json", **csrf_header(csrf_client)
    )
    assert refresh.status_code == 401
    csrf_client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
    assert csrf_client.get("/api/v1/auth/me/").status_code == 401


@pytest.mark.django_db
def test_login_and_refresh_throttling(csrf_client):
    headers = csrf_header(csrf_client)
    login_responses = [
        csrf_client.post(
            "/api/v1/auth/login/",
            {"email": "missing@example.com", "password": "bad-password"},
            format="json",
            **headers,
        )
        for _ in range(6)
    ]
    assert [response.status_code for response in login_responses[:5]] == [401] * 5
    assert login_responses[5].status_code == 429
    assert "Retry-After" in login_responses[5]

    refresh_responses = [
        csrf_client.post("/api/v1/auth/refresh/", {}, format="json", **headers) for _ in range(11)
    ]
    assert refresh_responses[9].status_code == 401
    assert refresh_responses[10].status_code == 429
