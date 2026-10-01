import yaml
from django.urls import reverse


def test_openapi_schema_is_generated_without_project_warnings(api_client):
    response = api_client.get(reverse("schema"))
    assert response.status_code == 200
    content = response.content.decode()
    assert "/api/v1/auth/login/" in content
    assert "password" in content
    assert "UserOutput" in content
    assert "/api/v1/products/" in content
    assert "/api/v1/admin/inventory/variants/{variant_id}/adjustments/" in content
    assert "/api/v1/events/" in content
    assert "/api/v1/cart/" in content
    assert "/api/v1/checkout/quote/" in content
    assert "/api/v1/orders/" in content
    assert "/api/v1/orders/{order_id}/payment/" in content
    assert "/api/v1/payments/vnpay/ipn/" in content
    assert "/api/v1/admin/orders/" in content
    assert "/api/v1/admin/orders/{order_id}/transitions/" in content

    schema = yaml.safe_load(content)
    assert "ApiError" in schema["components"]["schemas"]
    login_errors = schema["paths"]["/api/v1/auth/login/"]["post"]["responses"]
    for status_code in ("400", "401", "403", "429"):
        error_schema = login_errors[status_code]["content"]["application/json"]["schema"]
        assert error_schema["$ref"] == "#/components/schemas/ApiError"


def test_api_error_contains_request_id_and_preserves_header(api_client):
    response = api_client.get("/api/v1/auth/me/", HTTP_X_REQUEST_ID="client-request-123")
    assert response.status_code == 401
    assert response["X-Request-ID"] == "client-request-123"
    assert response.data["request_id"] == "client-request-123"
    assert {"code", "message", "details", "request_id"} == set(response.data)
    assert "WWW-Authenticate" in response
