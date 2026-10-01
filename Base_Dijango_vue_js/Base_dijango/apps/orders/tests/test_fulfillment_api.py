from uuid import uuid4

import pytest
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from apps.accounts.models import LoyaltyAccount, LoyaltyTransaction
from apps.accounts.roles import BusinessRole
from apps.accounts.tests.factories import AddressFactory, UserFactory
from apps.catalog.tests.factories import ProductVariantFactory
from apps.orders.models import Cart, CartItem, Order, OrderStatusHistory

pytestmark = pytest.mark.django_db


def create_cod_order():
    customer = UserFactory()
    customer.groups.add(Group.objects.get(name=BusinessRole.CUSTOMER))
    address = AddressFactory(user=customer)
    variant = ProductVariantFactory(inventory=5)
    item = CartItem.objects.create(
        cart=Cart.objects.create(user=customer), variant=variant, quantity=2
    )
    client = APIClient()
    client.force_authenticate(customer)
    response = client.post(
        "/api/v1/orders/",
        {"address_id": address.id, "cart_item_ids": [item.id]},
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid4()),
    )
    return Order.objects.get(pk=response.data["id"]), customer, variant


def test_staff_lists_and_transitions_cod_order_with_stale_protection():
    order, _, _ = create_cod_order()
    staff = UserFactory()
    staff.groups.add(Group.objects.get(name=BusinessRole.STAFF))
    client = APIClient()
    client.force_authenticate(staff)

    listed = client.get("/api/v1/admin/orders/?status=pending_confirmation")
    previous_updated_at = order.updated_at.isoformat()
    transitioned = client.post(
        f"/api/v1/admin/orders/{order.id}/transitions/",
        {
            "to_status": Order.Status.CONFIRMED,
            "expected_updated_at": previous_updated_at,
            "note": "Đã gọi xác nhận",
        },
        format="json",
    )
    stale = client.post(
        f"/api/v1/admin/orders/{order.id}/transitions/",
        {
            "to_status": Order.Status.PREPARING,
            "expected_updated_at": previous_updated_at,
        },
        format="json",
    )

    assert listed.status_code == 200
    assert listed.data["count"] == 1
    assert transitioned.status_code == 200
    assert transitioned.data["status"] == Order.Status.CONFIRMED
    assert stale.status_code == 409
    assert OrderStatusHistory.objects.filter(order=order, actor=staff).count() == 1


def test_customer_cannot_access_admin_order_queue():
    _, customer, _ = create_cod_order()
    client = APIClient()
    client.force_authenticate(customer)

    assert client.get("/api/v1/admin/orders/").status_code == 403


def test_staff_cancel_restores_cod_inventory():
    order, _, variant = create_cod_order()
    staff = UserFactory()
    staff.groups.add(Group.objects.get(name=BusinessRole.STAFF))
    client = APIClient()
    client.force_authenticate(staff)

    response = client.post(
        f"/api/v1/admin/orders/{order.id}/transitions/",
        {
            "to_status": Order.Status.CANCELLED,
            "expected_updated_at": order.updated_at.isoformat(),
            "note": "Khách yêu cầu hủy",
        },
        format="json",
    )

    assert response.status_code == 200
    variant.inventory.refresh_from_db()
    assert variant.inventory.quantity == 5


def test_customer_confirms_shipped_order_and_can_only_confirm_own_order():
    order, customer, _ = create_cod_order()
    Order.objects.filter(pk=order.pk).update(status=Order.Status.SHIPPED)
    client = APIClient()
    client.force_authenticate(customer)

    response = client.post(f"/api/v1/orders/{order.id}/confirm-received/")
    duplicate = client.post(f"/api/v1/orders/{order.id}/confirm-received/")

    assert response.status_code == 200
    assert response.data["status"] == Order.Status.COMPLETED
    assert response.data["payment_status"] == Order.PaymentStatus.PAID
    assert duplicate.status_code == 409
    assert OrderStatusHistory.objects.filter(
        order=order,
        actor=customer,
        to_status=Order.Status.COMPLETED,
    ).exists()
    account = LoyaltyAccount.objects.get(user=customer)
    assert account.balance == round(float(order.total) * 0.005)
    assert LoyaltyTransaction.objects.filter(order=order).count() == 1

    other_customer = UserFactory()
    other_customer.groups.add(Group.objects.get(name=BusinessRole.CUSTOMER))
    client.force_authenticate(other_customer)
    assert client.post(f"/api/v1/orders/{order.id}/confirm-received/").status_code == 404
