import pytest
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from apps.accounts.roles import BusinessRole
from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import ProductEvent
from apps.catalog.tests.factories import ProductVariantFactory
from apps.orders.models import CartItem

pytestmark = pytest.mark.django_db


def customer_client(user=None) -> tuple[APIClient, object]:
    user = user or UserFactory()
    group, _ = Group.objects.get_or_create(name=BusinessRole.CUSTOMER)
    user.groups.add(group)
    client = APIClient()
    client.force_authenticate(user)
    return client, user


def test_customer_adds_updates_and_removes_cart_item():
    variant = ProductVariantFactory(inventory=5)
    client, user = customer_client()

    created = client.post(
        "/api/v1/cart/items/", {"variant": variant.id, "quantity": 2}, format="json"
    )

    assert created.status_code == 201
    item_id = created.data["id"]
    assert created.data["line_total"] == "3000000"
    assert ProductEvent.objects.get(user=user).event_type == ProductEvent.EventType.ADD_CART

    updated = client.patch(f"/api/v1/cart/items/{item_id}/", {"quantity": 3}, format="json")
    cart = client.get("/api/v1/cart/")
    deleted = client.delete(f"/api/v1/cart/items/{item_id}/")

    assert updated.status_code == 200
    assert updated.data["quantity"] == 3
    assert cart.status_code == 200
    assert cart.data["item_count"] == 3
    assert cart.data["subtotal"] == "4500000"
    assert deleted.status_code == 204
    assert not CartItem.objects.filter(pk=item_id).exists()


def test_cart_rejects_quantity_above_stock_and_other_customer_item():
    variant = ProductVariantFactory(inventory=2)
    owner_client, _ = customer_client()
    created = owner_client.post(
        "/api/v1/cart/items/", {"variant": variant.id, "quantity": 2}, format="json"
    )
    other_client, _ = customer_client()

    over_stock = owner_client.patch(
        f"/api/v1/cart/items/{created.data['id']}/", {"quantity": 3}, format="json"
    )
    other_user_read = other_client.patch(
        f"/api/v1/cart/items/{created.data['id']}/", {"quantity": 1}, format="json"
    )

    assert over_stock.status_code == 400
    assert other_user_read.status_code == 404


def test_non_customer_cannot_use_cart():
    user = UserFactory()
    client = APIClient()
    client.force_authenticate(user)

    response = client.get("/api/v1/cart/")

    assert response.status_code == 403
