import pytest

from apps.accounts.tests.factories import AddressFactory, UserFactory


def address_payload(**overrides):
    payload = {
        "recipient_name": "Nguyễn Văn A",
        "phone_number": "0901234567",
        "province": "Hà Nội",
        "district": "Ba Đình",
        "ward": "Điện Biên",
        "street_address": "12 Đường Độc Lập",
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_address_crud_keeps_exactly_one_default(api_client):
    user = UserFactory()
    api_client.force_authenticate(user)

    first = api_client.post("/api/v1/account/addresses/", address_payload(), format="json")
    second = api_client.post(
        "/api/v1/account/addresses/",
        address_payload(recipient_name="Trần Văn B", street_address="34 Đường Mới"),
        format="json",
    )
    assert first.status_code == second.status_code == 201
    assert first.data["is_default"] is True
    assert second.data["is_default"] is False

    promoted = api_client.post(
        f"/api/v1/account/addresses/{second.data['id']}/set-default/", {}, format="json"
    )
    assert promoted.status_code == 200
    assert promoted.data["is_default"] is True

    deleted = api_client.delete(f"/api/v1/account/addresses/{second.data['id']}/")
    assert deleted.status_code == 204
    addresses = api_client.get("/api/v1/account/addresses/")
    assert len(addresses.data) == 1
    assert addresses.data[0]["is_default"] is True


@pytest.mark.django_db
def test_address_endpoints_enforce_ownership(api_client):
    owner = UserFactory()
    attacker = UserFactory()
    address = AddressFactory(user=owner, is_default=True)
    api_client.force_authenticate(attacker)

    assert api_client.get(f"/api/v1/account/addresses/{address.id}/").status_code == 404
    assert (
        api_client.patch(
            f"/api/v1/account/addresses/{address.id}/",
            {"recipient_name": "Attacker"},
            format="json",
        ).status_code
        == 404
    )
    assert api_client.delete(f"/api/v1/account/addresses/{address.id}/").status_code == 404
    address.refresh_from_db()
    assert address.recipient_name != "Attacker"


@pytest.mark.django_db
def test_address_validation_and_authentication(api_client):
    assert api_client.get("/api/v1/account/addresses/").status_code == 401
    api_client.force_authenticate(UserFactory())
    response = api_client.post(
        "/api/v1/account/addresses/",
        address_payload(phone_number="not-a-phone"),
        format="json",
    )
    assert response.status_code == 400
    assert "phone_number" in response.data["details"]
