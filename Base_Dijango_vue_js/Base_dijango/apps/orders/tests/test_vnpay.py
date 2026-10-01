from datetime import timedelta
from urllib.parse import parse_qsl, urlsplit
from uuid import uuid4

import pytest
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.roles import BusinessRole
from apps.accounts.tests.factories import AddressFactory, UserFactory
from apps.catalog.models import StockMovement
from apps.catalog.tests.factories import ProductVariantFactory
from apps.orders.models import (
    Cart,
    CartItem,
    InventoryReservation,
    Order,
    Payment,
    PaymentAttempt,
    PaymentEvent,
)
from apps.orders.payments import sign_vnpay_params

pytestmark = pytest.mark.django_db


@pytest.fixture
def vnpay_settings(settings):
    settings.VNPAY_PAYMENT_URL = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"
    settings.VNPAY_TMN_CODE = "TESTCODE"
    settings.VNPAY_HASH_SECRET = "test-secret"
    settings.VNPAY_RETURN_URL = "http://localhost:5173/payment/vnpay-return"
    settings.FRONTEND_BASE_URL = "http://localhost:5173"
    settings.VNPAY_VERSION = "2.1.0"
    settings.VNPAY_COMMAND = "pay"
    settings.VNPAY_ORDER_TYPE = "other"
    settings.PAYMENT_RESERVATION_MINUTES = 15


def create_vnpay_order():
    user = UserFactory()
    user.groups.add(Group.objects.get(name=BusinessRole.CUSTOMER))
    address = AddressFactory(user=user)
    variant = ProductVariantFactory(price=500_000, inventory=4)
    item = CartItem.objects.create(cart=Cart.objects.create(user=user), variant=variant, quantity=2)
    client = APIClient()
    client.force_authenticate(user)
    response = client.post(
        "/api/v1/orders/",
        {
            "address_id": address.id,
            "cart_item_ids": [item.id],
            "payment_method": Order.PaymentMethod.VNPAY,
        },
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid4()),
    )
    return client, Order.objects.get(pk=response.data["id"]), variant


def signed_ipn(attempt: PaymentAttempt, **overrides) -> dict[str, str]:
    params = {
        "vnp_TmnCode": "TESTCODE",
        "vnp_TxnRef": attempt.reference,
        "vnp_Amount": str(int(attempt.payment.amount * 100)),
        "vnp_ResponseCode": "00",
        "vnp_TransactionStatus": "00",
        "vnp_TransactionNo": "VNP123456",
    }
    params.update(overrides)
    params["vnp_SecureHash"] = sign_vnpay_params(params, "test-secret")
    return params


def test_vnpay_order_reserves_stock_and_attempt_is_idempotent(vnpay_settings):
    client, order, variant = create_vnpay_order()
    key = str(uuid4())

    first = client.post(
        f"/api/v1/orders/{order.id}/payment/",
        {"locale": "vn"},
        format="json",
        HTTP_IDEMPOTENCY_KEY=key,
    )
    second = client.post(
        f"/api/v1/orders/{order.id}/payment/",
        {"locale": "vn"},
        format="json",
        HTTP_IDEMPOTENCY_KEY=key,
    )
    conflict = client.post(
        f"/api/v1/orders/{order.id}/payment/",
        {"locale": "vn", "bank_code": "NCB"},
        format="json",
        HTTP_IDEMPOTENCY_KEY=key,
    )

    assert first.status_code == 201
    assert second.status_code == 200
    assert first.data["id"] == second.data["id"]
    assert conflict.status_code == 409
    variant.inventory.refresh_from_db()
    assert variant.inventory.quantity == 2
    assert InventoryReservation.objects.get().status == InventoryReservation.Status.ACTIVE
    assert StockMovement.objects.get().kind == StockMovement.Kind.RESERVATION
    query = dict(parse_qsl(urlsplit(first.data["checkout_url"]).query))
    signature = query.pop("vnp_SecureHash")
    assert signature == sign_vnpay_params(query, "test-secret")


def test_vnpay_accepts_same_origin_order_return_url(vnpay_settings):
    client, order, _ = create_vnpay_order()

    response = client.post(
        f"/api/v1/orders/{order.id}/payment/",
        {"return_url": f"http://localhost:5173/orders/{order.id}"},
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid4()),
    )

    assert response.status_code == 201
    query = dict(parse_qsl(urlsplit(response.data["checkout_url"]).query))
    assert query["vnp_ReturnUrl"] == f"http://localhost:5173/orders/{order.id}"


def test_vnpay_rejects_off_origin_return_url(vnpay_settings):
    client, order, _ = create_vnpay_order()

    response = client.post(
        f"/api/v1/orders/{order.id}/payment/",
        {"return_url": "https://malicious.example/steal"},
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid4()),
    )

    assert response.status_code == 409


def test_valid_vnpay_ipn_marks_paid_and_duplicate_is_safe(vnpay_settings):
    client, order, variant = create_vnpay_order()
    created = client.post(
        f"/api/v1/orders/{order.id}/payment/",
        {},
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid4()),
    )
    attempt = PaymentAttempt.objects.get(pk=created.data["id"])
    params = signed_ipn(attempt)

    first = APIClient().get("/api/v1/payments/vnpay/ipn/", params)
    duplicate = APIClient().get("/api/v1/payments/vnpay/ipn/", params)

    assert first.data["RspCode"] == "00"
    assert duplicate.data["RspCode"] == "02"
    order.refresh_from_db()
    attempt.payment.refresh_from_db()
    variant.inventory.refresh_from_db()
    assert order.status == Order.Status.CONFIRMED
    assert order.payment_status == Order.PaymentStatus.PAID
    assert attempt.payment.status == Order.PaymentStatus.PAID
    assert InventoryReservation.objects.get().status == InventoryReservation.Status.CAPTURED
    assert variant.inventory.quantity == 2
    assert PaymentEvent.objects.count() == 1


def test_signed_browser_return_confirms_payment_when_local_ipn_is_unavailable(vnpay_settings):
    client, order, variant = create_vnpay_order()
    created = client.post(
        f"/api/v1/orders/{order.id}/payment/",
        {},
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid4()),
    )
    attempt = PaymentAttempt.objects.get(pk=created.data["id"])

    response = client.post(
        f"/api/v1/orders/{order.id}/payment/vnpay-return/",
        {"params": signed_ipn(attempt)},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["payment_status"] == Order.PaymentStatus.PAID
    assert response.data["order_status"] == Order.Status.CONFIRMED
    variant.inventory.refresh_from_db()
    assert variant.inventory.quantity == 2
    assert InventoryReservation.objects.get().status == InventoryReservation.Status.CAPTURED


def test_vnpay_return_rejects_attempt_from_another_customer(vnpay_settings):
    _, order, _ = create_vnpay_order()
    attempt = PaymentAttempt.objects.create(
        payment=Payment.objects.get(order=order),
        idempotency_key=uuid4(),
        request_fingerprint="test",
        reference=uuid4().hex,
        expires_at=timezone.now() + timedelta(minutes=5),
    )
    other_customer = UserFactory()
    other_customer.groups.add(Group.objects.get(name=BusinessRole.CUSTOMER))
    client = APIClient()
    client.force_authenticate(other_customer)

    response = client.post(
        f"/api/v1/orders/{order.id}/payment/vnpay-return/",
        {"params": signed_ipn(attempt)},
        format="json",
    )

    assert response.status_code == 404


def test_vnpay_rejects_bad_signature_and_amount(vnpay_settings):
    client, order, _ = create_vnpay_order()
    created = client.post(
        f"/api/v1/orders/{order.id}/payment/",
        {},
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid4()),
    )
    attempt = PaymentAttempt.objects.get(pk=created.data["id"])
    bad_signature = signed_ipn(attempt)
    bad_signature["vnp_SecureHash"] = "invalid"
    bad_amount = signed_ipn(attempt, vnp_Amount="1")

    assert APIClient().get("/api/v1/payments/vnpay/ipn/", bad_signature).data["RspCode"] == "97"
    assert APIClient().get("/api/v1/payments/vnpay/ipn/", bad_amount).data["RspCode"] == "04"
    attempt.payment.refresh_from_db()
    assert attempt.payment.status == Order.PaymentStatus.PENDING


def test_invalid_signature_does_not_block_later_valid_ipn(vnpay_settings):
    client, order, _ = create_vnpay_order()
    created = client.post(
        f"/api/v1/orders/{order.id}/payment/",
        {},
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid4()),
    )
    attempt = PaymentAttempt.objects.get(pk=created.data["id"])
    valid = signed_ipn(attempt)
    invalid = {**valid, "vnp_SecureHash": "invalid"}

    assert APIClient().get("/api/v1/payments/vnpay/ipn/", invalid).data["RspCode"] == "97"
    assert APIClient().get("/api/v1/payments/vnpay/ipn/", valid).data["RspCode"] == "00"

    order.refresh_from_db()
    assert order.payment_status == Order.PaymentStatus.PAID


def test_customer_cancel_releases_vnpay_reservation_and_attempt(vnpay_settings):
    client, order, variant = create_vnpay_order()
    created = client.post(
        f"/api/v1/orders/{order.id}/payment/",
        {},
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid4()),
    )

    response = client.post(f"/api/v1/orders/{order.id}/cancel/")

    assert response.status_code == 200
    order.refresh_from_db()
    variant.inventory.refresh_from_db()
    attempt = PaymentAttempt.objects.get(pk=created.data["id"])
    assert order.payment_status == Order.PaymentStatus.CANCELLED
    assert Payment.objects.get(order=order).status == Order.PaymentStatus.CANCELLED
    assert attempt.status == PaymentAttempt.Status.CANCELLED
    assert variant.inventory.quantity == 4


def test_failed_ipn_and_expiry_release_inventory(vnpay_settings):
    client, order, variant = create_vnpay_order()
    created = client.post(
        f"/api/v1/orders/{order.id}/payment/",
        {},
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid4()),
    )
    attempt = PaymentAttempt.objects.get(pk=created.data["id"])
    failed = signed_ipn(attempt, vnp_ResponseCode="24", vnp_TransactionStatus="02")

    response = APIClient().get("/api/v1/payments/vnpay/ipn/", failed)

    assert response.data["RspCode"] == "00"
    order.refresh_from_db()
    variant.inventory.refresh_from_db()
    assert order.status == Order.Status.CANCELLED
    assert order.payment_status == Order.PaymentStatus.FAILED
    assert variant.inventory.quantity == 4

    client, order, variant = create_vnpay_order()
    InventoryReservation.objects.filter(order_item__order=order).update(
        expires_at=timezone.now() - timedelta(seconds=1)
    )
    call_command("release_expired_reservations", verbosity=0)
    order.refresh_from_db()
    variant.inventory.refresh_from_db()
    assert order.status == Order.Status.CANCELLED
    assert variant.inventory.quantity == 4
    assert Payment.objects.get(order=order).status == Order.PaymentStatus.FAILED
