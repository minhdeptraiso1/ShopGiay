import uuid
from datetime import timedelta

import pytest
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import LoyaltyAccount
from apps.accounts.roles import BusinessRole
from apps.accounts.tests.factories import AddressFactory, UserFactory
from apps.catalog.models import ProductEvent
from apps.catalog.tests.factories import ProductFactory, ProductVariantFactory
from apps.engagement.models import Banner, Review, Voucher, VoucherUsage, WishlistItem
from apps.orders.models import Cart, CartItem, Order
from apps.orders.services import create_order

pytestmark = pytest.mark.django_db


def client_for(role: BusinessRole) -> tuple[APIClient, object]:
    user = UserFactory()
    group, _ = Group.objects.get_or_create(name=role)
    user.groups.add(group)
    client = APIClient()
    client.force_authenticate(user)
    return client, user


def test_voucher_is_recalculated_and_allocated_when_order_is_created():
    client, user = client_for(BusinessRole.CUSTOMER)
    address = AddressFactory(user=user)
    variant = ProductVariantFactory(price=500_000, inventory=5)
    cart = Cart.objects.create(user=user)
    item = CartItem.objects.create(cart=cart, variant=variant, quantity=2)
    Voucher.objects.create(
        code="SALE10",
        name="Giảm 10%",
        discount_type=Voucher.DiscountType.PERCENT,
        value=10,
        min_order_value=500_000,
        starts_at=timezone.now() - timedelta(days=1),
        ends_at=timezone.now() + timedelta(days=1),
        usage_limit=10,
        per_user_limit=1,
    )

    quote = client.post(
        "/api/v1/checkout/quote/",
        {"address_id": address.id, "cart_item_ids": [item.id], "voucher_code": "sale10"},
        format="json",
    )
    order_response = client.post(
        "/api/v1/orders/",
        {
            "address_id": address.id,
            "cart_item_ids": [item.id],
            "voucher_code": "SALE10",
            "payment_method": "cod",
        },
        format="json",
        HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
    )

    assert quote.status_code == 200
    assert quote.data["discount_total"] == "100000"
    assert quote.data["total"] == "900000"
    assert order_response.status_code == 201
    order = Order.objects.get(pk=order_response.data["id"])
    assert order.discount_total == 100_000
    assert order.items.get().discount_total == 100_000
    usage = VoucherUsage.objects.get(order=order)
    assert usage.status == VoucherUsage.Status.REDEEMED
    assert sum(allocation.amount for allocation in usage.allocations.all()) == 100_000


def test_eligible_vouchers_are_selected_by_points_and_current_cart():
    client, user = client_for(BusinessRole.CUSTOMER)
    address = AddressFactory(user=user)
    variant = ProductVariantFactory(price=500_000, inventory=5)
    cart = Cart.objects.create(user=user)
    item = CartItem.objects.create(cart=cart, variant=variant, quantity=1)
    Voucher.objects.create(
        code="POINT100",
        name="Ưu đãi thành viên",
        discount_type=Voucher.DiscountType.FIXED,
        value=50_000,
        required_points=100,
        starts_at=timezone.now() - timedelta(days=1),
        ends_at=timezone.now() + timedelta(days=1),
    )
    payload = {"address_id": address.id, "cart_item_ids": [item.id]}

    before = client.post("/api/v1/vouchers/eligible/", payload, format="json")
    LoyaltyAccount.objects.create(user=user, balance=100)
    after = client.post("/api/v1/vouchers/eligible/", payload, format="json")

    assert before.status_code == 200
    assert before.data["vouchers"] == []
    assert after.data["points_balance"] == 100
    assert after.data["vouchers"][0]["code"] == "POINT100"


def test_wishlist_toggle_is_owned_and_records_server_event():
    client, user = client_for(BusinessRole.CUSTOMER)
    product = ProductFactory()
    ProductVariantFactory(product=product, inventory=2)

    added = client.post("/api/v1/wishlist/", {"product": product.id}, format="json")
    listed = client.get("/api/v1/wishlist/")
    removed = client.post("/api/v1/wishlist/", {"product": product.id}, format="json")

    assert added.data == {"product_id": product.id, "is_wishlisted": True}
    assert listed.status_code == 200
    assert listed.data[0]["product"]["id"] == product.id
    assert removed.data["is_wishlisted"] is False
    assert not WishlistItem.objects.filter(user=user, product=product).exists()
    assert list(ProductEvent.objects.values_list("event_type", flat=True)) == [
        ProductEvent.EventType.WISHLIST_REMOVE,
        ProductEvent.EventType.WISHLIST_ADD,
    ]


@pytest.mark.django_db(transaction=True)
def test_review_requires_completed_purchase_and_staff_moderation():
    customer_client, user = client_for(BusinessRole.CUSTOMER)
    address = AddressFactory(user=user)
    variant = ProductVariantFactory(price=800_000, inventory=3)
    cart = Cart.objects.create(user=user)
    cart_item = CartItem.objects.create(cart=cart, variant=variant, quantity=1)
    order, _ = create_order(
        user=user,
        address_id=address.id,
        cart_item_ids=[cart_item.id],
        idempotency_key=uuid.uuid4(),
    )
    order.status = Order.Status.COMPLETED
    order.save(update_fields=["status", "updated_at"])
    order_item = order.items.get()

    created = customer_client.post(
        f"/api/v1/products/{variant.product_id}/reviews/",
        {"order_item": order_item.id, "rating": 5, "content": "Giày rất êm và đúng kích cỡ."},
        format="json",
    )
    public_before = APIClient().get(f"/api/v1/products/{variant.product_id}/reviews/")
    staff_client, _ = client_for(BusinessRole.STAFF)
    moderated = staff_client.post(
        f"/api/v1/admin/reviews/{created.data['id']}/moderate/",
        {"status": "approved", "moderation_note": "Nội dung hợp lệ"},
        format="json",
    )
    public_after = APIClient().get(f"/api/v1/products/{variant.product_id}/reviews/")

    assert created.status_code == 201
    assert created.data["status"] == Review.Status.PENDING
    assert public_before.data == []
    assert moderated.status_code == 200
    assert public_after.data[0]["rating"] == 5


def test_only_active_scheduled_banners_are_public_and_admin_can_manage():
    now = timezone.now()
    Banner.objects.create(
        title="Đang chạy",
        image_url="https://example.com/live.jpg",
        position=Banner.Position.HOME_STRIP,
        starts_at=now - timedelta(hours=1),
        ends_at=now + timedelta(hours=1),
    )
    Banner.objects.create(
        title="Đã hết hạn",
        image_url="https://example.com/expired.jpg",
        position=Banner.Position.HOME_STRIP,
        starts_at=now - timedelta(days=2),
        ends_at=now - timedelta(days=1),
    )

    response = APIClient().get("/api/v1/banners/?position=home_strip")
    customer_client, _ = client_for(BusinessRole.CUSTOMER)
    denied = customer_client.post(
        "/api/v1/admin/banners/",
        {
            "title": "Không hợp lệ",
            "image_url": "https://example.com/x.jpg",
            "position": "home_strip",
            "starts_at": now,
            "ends_at": now + timedelta(days=1),
        },
        format="json",
    )

    assert response.status_code == 200
    assert [item["title"] for item in response.data] == ["Đang chạy"]
    assert denied.status_code == 403
