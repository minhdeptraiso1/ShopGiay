from django.urls import reverse


def test_openapi_schema_is_generated_without_project_warnings(api_client):
    response = api_client.get(reverse("schema"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "/api/v1/auth/login/" in content
    assert "password" in content
    assert "UserOutput" in content


def test_api_error_contains_request_id_and_preserves_header(api_client):
    response = api_client.get("/api/v1/auth/me/", HTTP_X_REQUEST_ID="client-request-123")
    assert response.status_code == 401
    assert response["X-Request-ID"] == "client-request-123"
    assert response.data["request_id"] == "client-request-123"
    assert {"code", "message", "details", "request_id"} == set(response.data)
    assert "WWW-Authenticate" in response
