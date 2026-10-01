import uuid

from django.conf import settings
from django.db import models
from django.db.models import F, Q

from apps.accounts.models import Address
from apps.catalog.models import ProductVariant


class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Cart {self.user_id}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT, related_name="cart_items")
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at", "id"]
        constraints = [
            models.UniqueConstraint(fields=["cart", "variant"], name="orders_cart_variant_uniq"),
            models.CheckConstraint(condition=Q(quantity__gt=0), name="orders_cart_quantity_gt_0"),
        ]

    def __str__(self) -> str:
        return f"{self.cart_id}:{self.variant.sku} x {self.quantity}"


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING_CONFIRMATION = "pending_confirmation", "Chờ xác nhận"
        CONFIRMED = "confirmed", "Đã xác nhận"
        PREPARING = "preparing", "Đang chuẩn bị"
        SHIPPED = "shipped", "Đang giao"
        COMPLETED = "completed", "Hoàn tất"
        CANCELLED = "cancelled", "Đã hủy"

    class PaymentMethod(models.TextChoices):
        COD = "cod", "Thanh toán khi nhận hàng"
        VNPAY = "vnpay", "Thanh toán VNPay"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Chờ thanh toán"
        PAID = "paid", "Đã thanh toán"
        FAILED = "failed", "Thất bại"
        CANCELLED = "cancelled", "Đã hủy"
        REFUNDED = "refunded", "Đã hoàn tiền"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders"
    )
    address = models.ForeignKey(
        Address, null=True, blank=True, on_delete=models.SET_NULL, related_name="orders"
    )
    number = models.CharField(max_length=32, unique=True)
    idempotency_key = models.UUIDField(default=uuid.uuid4)
    request_fingerprint = models.CharField(max_length=64)
    status = models.CharField(
        max_length=24, choices=Status.choices, default=Status.PENDING_CONFIRMATION, db_index=True
    )
    payment_method = models.CharField(
        max_length=12, choices=PaymentMethod.choices, default=PaymentMethod.COD
    )
    payment_status = models.CharField(
        max_length=16, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    currency = models.CharField(max_length=3, default="VND")
    subtotal = models.DecimalField(max_digits=14, decimal_places=0)
    shipping_fee = models.DecimalField(max_digits=14, decimal_places=0)
    discount_total = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    total = models.DecimalField(max_digits=14, decimal_places=0)
    recipient_name = models.CharField(max_length=120)
    phone_number = models.CharField(max_length=20)
    province = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "idempotency_key"], name="orders_user_idempotency_key_uniq"
            ),
            models.CheckConstraint(
                condition=Q(subtotal__gte=0)
                & Q(shipping_fee__gte=0)
                & Q(discount_total__gte=0)
                & Q(total__gte=0),
                name="orders_amounts_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(total=F("subtotal") + F("shipping_fee") - F("discount_total")),
                name="orders_total_matches_components",
            ),
            models.CheckConstraint(condition=Q(currency="VND"), name="orders_currency_vnd"),
        ]
        indexes = [models.Index(fields=["user", "status", "-created_at"])]

    def __str__(self) -> str:
        return self.number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="items")
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.PositiveIntegerField()
    product_name = models.CharField(max_length=200)
    product_slug = models.SlugField(max_length=220)
    sku = models.CharField(max_length=64)
    size_label = models.CharField(max_length=40)
    color_name = models.CharField(max_length=80)
    unit_price = models.DecimalField(max_digits=14, decimal_places=0)
    discount_total = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    line_total = models.DecimalField(max_digits=14, decimal_places=0)
    currency = models.CharField(max_length=3, default="VND")

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(fields=["order", "variant"], name="orders_order_variant_uniq"),
            models.CheckConstraint(condition=Q(quantity__gt=0), name="orders_item_quantity_gt_0"),
            models.CheckConstraint(
                condition=Q(unit_price__gte=0) & Q(discount_total__gte=0) & Q(line_total__gte=0),
                name="orders_item_amounts_gte_0",
            ),
            models.CheckConstraint(
                condition=Q(line_total=F("unit_price") * F("quantity") - F("discount_total")),
                name="orders_item_total_matches_components",
            ),
            models.CheckConstraint(condition=Q(currency="VND"), name="orders_item_currency_vnd"),
        ]

    def __str__(self) -> str:
        return f"{self.order.number}: {self.sku} x {self.quantity}"


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="status_history")
    from_status = models.CharField(max_length=24, choices=Order.Status.choices, blank=True)
    to_status = models.CharField(max_length=24, choices=Order.Status.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="order_status_changes",
    )
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self) -> str:
        return f"{self.order.number}: {self.from_status} -> {self.to_status}"


class Payment(models.Model):
    class Provider(models.TextChoices):
        VNPAY = "vnpay", "VNPay"

    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="payment")
    provider = models.CharField(max_length=20, choices=Provider.choices)
    status = models.CharField(
        max_length=16, choices=Order.PaymentStatus.choices, default=Order.PaymentStatus.PENDING
    )
    amount = models.DecimalField(max_digits=14, decimal_places=0)
    currency = models.CharField(max_length=3, default="VND")
    provider_transaction_no = models.CharField(max_length=64, blank=True, db_index=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(amount__gte=0), name="orders_payment_amount_gte_0"),
            models.CheckConstraint(condition=Q(currency="VND"), name="orders_payment_currency_vnd"),
            models.UniqueConstraint(
                fields=["provider", "provider_transaction_no"],
                condition=~Q(provider_transaction_no=""),
                name="orders_payment_provider_transaction_uniq",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.order.number}:{self.provider}:{self.status}"


class PaymentAttempt(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Chờ thanh toán"
        SUCCEEDED = "succeeded", "Thành công"
        FAILED = "failed", "Thất bại"
        EXPIRED = "expired", "Hết hạn"
        CANCELLED = "cancelled", "Đã hủy"

    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name="attempts")
    idempotency_key = models.UUIDField()
    request_fingerprint = models.CharField(max_length=64)
    reference = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    checkout_url = models.TextField(blank=True)
    expires_at = models.DateTimeField()
    response_code = models.CharField(max_length=8, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["payment", "idempotency_key"],
                name="orders_payment_attempt_idempotency_uniq",
            )
        ]

    def __str__(self) -> str:
        return f"{self.reference}:{self.status}"


class PaymentEvent(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name="events")
    attempt = models.ForeignKey(
        PaymentAttempt, on_delete=models.PROTECT, related_name="events", null=True, blank=True
    )
    provider = models.CharField(max_length=20, choices=Payment.Provider.choices)
    event_key = models.CharField(max_length=64, unique=True)
    response_code = models.CharField(max_length=8, blank=True)
    transaction_status = models.CharField(max_length=8, blank=True)
    signature_valid = models.BooleanField(default=False)
    outcome = models.CharField(max_length=32)
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-received_at", "-id"]

    def __str__(self) -> str:
        return f"{self.provider}:{self.event_key}:{self.outcome}"


class InventoryReservation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Đang giữ"
        CAPTURED = "captured", "Đã thanh toán"
        RELEASED = "released", "Đã hoàn tồn"

    order_item = models.OneToOneField(
        OrderItem, on_delete=models.PROTECT, related_name="reservation"
    )
    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="inventory_reservations"
    )
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    expires_at = models.DateTimeField(db_index=True)
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(quantity__gt=0), name="orders_reservation_quantity_gt_0"
            )
        ]

    def __str__(self) -> str:
        return f"{self.order_item.order.number}:{self.variant.sku}:{self.status}"
