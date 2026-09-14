from unittest.mock import patch

import pytest


def test_liveness_does_not_check_dependencies(api_client):
    with patch("django.db.connections.__getitem__") as database:
        response = api_client.get("/health/live/")
    assert response.status_code == 200
    assert response.data == {"status": "ok"}
    database.assert_not_called()


@pytest.mark.django_db
def test_readiness_reports_dependencies_without_credentials(api_client):
    response = api_client.get("/health/ready/")
    assert response.status_code in {200, 503}
    assert set(response.data["checks"]) == {"database", "redis"}
    assert "url" not in response.data
    assert "password" not in response.data


@pytest.mark.django_db
def test_readiness_returns_503_when_redis_fails(api_client):
    with patch("apps.health.views.cache.set", side_effect=ConnectionError):
        response = api_client.get("/health/ready/")
    assert response.status_code == 503
    assert response.data["checks"]["redis"] is False
