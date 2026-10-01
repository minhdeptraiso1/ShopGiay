from uuid import uuid4

import pytest
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from apps.accounts.roles import BusinessRole
from apps.accounts.tests.factories import AddressFactory, UserFactory
from apps.catalog.models import StockMovement
from apps.catalog.tests.factories import ProductVariantFactory
from apps.orders.models import Cart, CartItem, Order, OrderStatusHistory

pytestmark = pytest.mark.django_db


def setup_checkout(*, price=600_000, stock=5, quantity=2):
    user = UserFactory()
    group, _ = Group.objects.get_or_create(name=BusinessRole.CUSTOMER)
    user.groups.add(group)
    address = AddressFactory(user=user)
    variant = ProductVariantFactory(price=price, inventory=stock)
    cart = Cart.objects.create(user=user)
    item = CartItem.objects.create(cart=cart, variant=variant, quantity=quantity)
    client = APIClient()
    client.force_authenticate(user)
    payload = {"address_id": address.id, "cart_item_ids": [item.id]}
    return client, user, address, variant, item, payload


def test_quote_uses_current_backend_price_and_shipping_settings(settings):
    settings.SHIPPING_FLAT_FEE = 30_000
    settings.FREE_SHIPPING_THRESHOLD = 1_000_000
    client, _, _, variant, item, payload = setup_checkout(price=400_000, quantity=2)
    variant.price = 450_000
    variant.save(update_fields=["price"])

    response = client.post("/api/v1/checkout/quote/", payload, format="json")

    assert response.status_code == 200
    assert response.data["lines"][0]["cart_item_id"] == item.id
    assert response.data["subtotal"] == "900000"
    assert response.data["shipping_fee"] == "30000"
    assert response.data["total"] == "930000"


def test_create_cod_order_is_idempotent_and_snapshots_then_deducts_stock(settings):
    settings.FREE_SHIPPING_THRESHOLD = 1_000_000
    client, user, address, variant, item, payload = setup_checkout()
    key = str(uuid4())

    first = client.post("/api/v1/orders/", payload, format="json", HTTP_IDEMPOTENCY_KEY=key)
    second = client.post("/api/v1/orders/", payload, format="json", HTTP_IDEMPOTENCY_KEY=key)

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.data["id"] == second.data["id"]
    assert Order.objects.count() == 1
    order = Order.objects.get()
    assert order.recipient_name == address.recipient_name
    assert order.items.get().sku == variant.sku
    assert order.items.get().unit_price == variant.price
    variant.inventory.refresh_from_db()
    assert variant.inventory.quantity == 3
    movement = StockMovement.objects.get(kind=StockMovement.Kind.SALE)
    assert (movement.quantity_before, movement.quantity_after, movement.actor) == (5, 3, user)
    assert not CartItem.objects.filter(pk=item.id).exists()
    assert OrderStatusHistory.objects.get().to_status == Order.Status.PENDING_CONFIRMATION


def test_same_idempotency_key_with_different_request_returns_conflict():
    client, user, address, _, _, payload = setup_checkout()
    key = str(uuid4())
    first = client.post("/api/v1/orders/", payload, format="json", HTTP_IDEMPOTENCY_KEY=key)
    other_variant = ProductVariantFactory(inventory=3)
    cart = Cart.objects.get(user=user)
    other_item = CartItem.objects.create(cart=cart, variant=other_variant, quantity=1)

    conflict = client.post(
        "/api/v1/orders/",
        {"address_id": address.id, "cart_item_ids": [other_item.id]},
        format="json",
        HTTP_IDEMPOTENCY_KEY=key,
    )

    assert first.status_code == 201
    assert conflict.status_code == 409
    assert Order.objects.count() == 1


def test_order_fails_atomically_when_stock_is_insufficient():
    client, _, _, variant, item, payload = setup_checkout(stock=1, quantity=2)

    response = client.post(
        "/api/v1/orders/", payload, format="json", HTTP_IDEMPOTENCY_KEY=str(uuid4())
    )

    assert response.status_code == 400
    assert Order.objects.count() == 0
    assert CartItem.objects.filter(pk=item.id).exists()
    variant.inventory.refresh_from_db()
    assert variant.inventory.quantity == 1
    assert not StockMovement.objects.filter(kind=StockMovement.Kind.SALE).exists()


def test_customer_cancel_restores_stock_once_and_other_user_cannot_see_order():
    client, _, _, variant, _, payload = setup_checkout(stock=4, quantity=2)
    created = client.post(
        "/api/v1/orders/", payload, format="json", HTTP_IDEMPOTENCY_KEY=str(uuid4())
    )
    order_id = created.data["id"]
    cancelled = client.post(f"/api/v1/orders/{order_id}/cancel/")
    repeated = client.post(f"/api/v1/orders/{order_id}/cancel/")

    other_client = APIClient()
    other_user = UserFactory()
    other_user.groups.add(Group.objects.get(name=BusinessRole.CUSTOMER))
    other_client.force_authenticate(other_user)
    hidden = other_client.get(f"/api/v1/orders/{order_id}/")

    assert cancelled.status_code == 200
    assert cancelled.data["status"] == Order.Status.CANCELLED
    assert repeated.status_code == 409
    assert hidden.status_code == 404
    variant.inventory.refresh_from_db()
    assert variant.inventory.quantity == 4
    assert StockMovement.objects.filter(kind=StockMovement.Kind.CANCELLATION).count() == 1


def test_order_requires_valid_idempotency_header():
    client, _, _, _, _, payload = setup_checkout()

    response = client.post("/api/v1/orders/", payload, format="json")

    assert response.status_code == 400
