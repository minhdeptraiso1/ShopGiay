from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.roles import BusinessRole
from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import StockMovement
from apps.catalog.tests.factories import ProductVariantFactory, SizeFactory
from apps.exchanges.models import ExchangeRequest, ExchangeReservation
from apps.orders.models import Order, OrderItem, OrderStatusHistory

pytestmark = pytest.mark.django_db


def make_user(role: str):
    user = UserFactory()
    user.groups.add(Group.objects.get(name=role))
    return user


def make_completed_order():
    customer = make_user(BusinessRole.CUSTOMER)
    source = ProductVariantFactory(inventory=0)
    target = ProductVariantFactory(
        product=source.product,
        size=SizeFactory(brand=source.product.brand),
        inventory=5,
    )
    order = Order.objects.create(
        user=customer,
        number=f"HD-{uuid4().hex[:12].upper()}",
        idempotency_key=uuid4(),
        request_fingerprint="test",
        status=Order.Status.COMPLETED,
        payment_method=Order.PaymentMethod.COD,
        payment_status=Order.PaymentStatus.PAID,
        subtotal=Decimal("3000000"),
        shipping_fee=0,
        total=Decimal("3000000"),
        recipient_name="Nguyễn Văn A",
        phone_number="0901234567",
        province="Hà Nội",
        district="Ba Đình",
        ward="Điện Biên",
        street_address="1 Đường Mẫu",
    )
    item = OrderItem.objects.create(
        order=order,
        variant=source,
        quantity=2,
        product_name=source.product.name,
        product_slug=source.product.slug,
        sku=source.sku,
        size_label=source.size.label,
        color_name=source.color.name,
        unit_price=Decimal("1500000"),
        line_total=Decimal("3000000"),
    )
    OrderStatusHistory.objects.create(
        order=order,
        from_status=Order.Status.SHIPPED,
        to_status=Order.Status.COMPLETED,
        actor=customer,
    )
    return customer, order, item, source, target


def create_exchange(client, order, item, target, *, key=None):
    return client.post(
        "/api/v1/exchanges/",
        {
            "order_id": order.id,
            "reason": "Cần đổi sang size phù hợp hơn",
            "items": [
                {
                    "order_item_id": item.id,
                    "target_variant_id": target.id,
                    "quantity": 1,
                }
            ],
        },
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(key or uuid4()),
    )


def test_customer_creates_and_retries_exchange_idempotently(settings):
    settings.EXCHANGE_WINDOW_DAYS = 30
    customer, order, item, _, target = make_completed_order()
    client = APIClient()
    client.force_authenticate(customer)
    key = uuid4()

    first = create_exchange(client, order, item, target, key=key)
    retry = create_exchange(client, order, item, target, key=key)
    changed = client.post(
        "/api/v1/exchanges/",
        {
            "order_id": order.id,
            "reason": "Nội dung khác với yêu cầu ban đầu",
            "items": [{"order_item_id": item.id, "target_variant_id": target.id, "quantity": 1}],
        },
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(key),
    )

    assert first.status_code == 201
    assert retry.status_code == 200
    assert retry.data["id"] == first.data["id"]
    assert changed.status_code == 409


def test_staff_completes_exchange_and_inventory_is_audited(settings):
    settings.EXCHANGE_WINDOW_DAYS = 30
    settings.EXCHANGE_RESERVATION_MINUTES = 60
    customer, order, item, source, target = make_completed_order()
    customer_client = APIClient()
    customer_client.force_authenticate(customer)
    created = create_exchange(customer_client, order, item, target)
    exchange_id = created.data["id"]

    staff = make_user(BusinessRole.STAFF)
    client = APIClient()
    client.force_authenticate(staff)

    def transition(payload):
        current = client.get(f"/api/v1/admin/exchanges/{exchange_id}/").data
        return client.post(
            f"/api/v1/admin/exchanges/{exchange_id}/transitions/",
            {"expected_updated_at": current["updated_at"], **payload},
            format="json",
        )

    approved = transition({"action": "approve"})
    exchange_item_id = approved.data["items"][0]["id"]
    received = transition(
        {
            "action": "receive",
            "received_items": [{"item_id": exchange_item_id, "received_quantity": 1}],
        }
    )
    inspected = transition(
        {
            "action": "inspect",
            "inspected_items": [
                {
                    "item_id": exchange_item_id,
                    "accepted_quantity": 1,
                    "disposition": "restock",
                }
            ],
        }
    )
    prepared = transition({"action": "prepare", "tracking_number": "GHN-001"})
    shipped = transition({"action": "ship", "tracking_number": "GHN-001"})
    completed = customer_client.post(f"/api/v1/exchanges/{exchange_id}/confirm-received/")

    assert [
        approved.status_code,
        received.status_code,
        inspected.status_code,
        prepared.status_code,
        shipped.status_code,
        completed.status_code,
    ] == [200, 200, 200, 200, 200, 200]
    assert shipped.data["status"] == ExchangeRequest.Status.REPLACEMENT_SHIPPED
    assert completed.data["status"] == ExchangeRequest.Status.COMPLETED
    source.inventory.refresh_from_db()
    target.inventory.refresh_from_db()
    assert source.inventory.quantity == 1
    assert target.inventory.quantity == 4
    assert set(StockMovement.objects.values_list("kind", flat=True)) >= {
        StockMovement.Kind.EXCHANGE_RESERVATION,
        StockMovement.Kind.EXCHANGE_RETURN,
    }


def test_expired_exchange_releases_reserved_stock(settings):
    settings.EXCHANGE_WINDOW_DAYS = 30
    customer, order, item, _, target = make_completed_order()
    customer_client = APIClient()
    customer_client.force_authenticate(customer)
    created = create_exchange(customer_client, order, item, target)
    staff = make_user(BusinessRole.STAFF)
    client = APIClient()
    client.force_authenticate(staff)
    client.post(
        f"/api/v1/admin/exchanges/{created.data['id']}/transitions/",
        {"action": "approve", "expected_updated_at": created.data["updated_at"]},
        format="json",
    )
    ExchangeRequest.objects.filter(pk=created.data["id"]).update(
        reservation_expires_at=timezone.now() - timedelta(seconds=1)
    )
    ExchangeReservation.objects.filter(exchange_item__exchange_id=created.data["id"]).update(
        expires_at=timezone.now() - timedelta(seconds=1)
    )

    call_command("release_expired_exchanges", verbosity=0)

    target.inventory.refresh_from_db()
    exchange = ExchangeRequest.objects.get(pk=created.data["id"])
    assert target.inventory.quantity == 5
    assert exchange.status == ExchangeRequest.Status.CANCELLED


def test_customer_cannot_access_admin_exchange_queue(settings):
    settings.EXCHANGE_WINDOW_DAYS = 30
    customer, _, _, _, _ = make_completed_order()
    client = APIClient()
    client.force_authenticate(customer)

    assert client.get("/api/v1/admin/exchanges/").status_code == 403
