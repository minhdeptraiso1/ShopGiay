import uuid

from django.conf import settings
from django.db import models
from django.db.models import F, Q


class ExchangeRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Chờ duyệt"
        APPROVED = "approved", "Đã duyệt"
        RECEIVED = "received", "Đã nhận hàng"
        INSPECTED = "inspected", "Đã kiểm hàng"
        REPLACEMENT_READY = "replacement_ready", "Sẵn sàng giao đổi"
        REPLACEMENT_SHIPPED = "replacement_shipped", "Đang giao hàng đổi"
        COMPLETED = "completed", "Hoàn tất"
        REJECTED = "rejected", "Từ chối"
        CANCELLED = "cancelled", "Đã hủy"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="exchange_requests"
    )
    order = models.ForeignKey(
        "orders.Order", on_delete=models.PROTECT, related_name="exchange_requests"
    )
    idempotency_key = models.UUIDField(default=uuid.uuid4)
    request_fingerprint = models.CharField(max_length=64)
    status = models.CharField(
        max_length=24, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    reason = models.CharField(max_length=500)
    evidence_url = models.URLField(max_length=500, blank=True)
    customer_note = models.TextField(max_length=1000, blank=True)
    staff_note = models.TextField(max_length=1000, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_exchanges",
    )
    reservation_expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "idempotency_key"], name="exchanges_user_idempotency_uniq"
            )
        ]
        indexes = [models.Index(fields=["status", "-created_at"])]

    def __str__(self) -> str:
        return f"EX-{self.pk or 'new'} / {self.order.number}"


class ExchangeItem(models.Model):
    class Disposition(models.TextChoices):
        PENDING = "pending", "Chưa kiểm"
        RESTOCK = "restock", "Có thể bán lại"
        DAMAGED = "damaged", "Hàng lỗi"

    exchange = models.ForeignKey(ExchangeRequest, on_delete=models.PROTECT, related_name="items")
    order_item = models.ForeignKey(
        "orders.OrderItem", on_delete=models.PROTECT, related_name="exchange_items"
    )
    target_variant = models.ForeignKey(
        "catalog.ProductVariant", on_delete=models.PROTECT, related_name="exchange_targets"
    )
    quantity = models.PositiveIntegerField()
    received_quantity = models.PositiveIntegerField(default=0)
    accepted_quantity = models.PositiveIntegerField(default=0)
    disposition = models.CharField(
        max_length=16, choices=Disposition.choices, default=Disposition.PENDING
    )
    inspection_note = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["id"]
        constraints = [
            models.UniqueConstraint(
                fields=["exchange", "order_item"], name="exchanges_request_order_item_uniq"
            ),
            models.CheckConstraint(condition=Q(quantity__gt=0), name="exchanges_item_qty_gt_0"),
            models.CheckConstraint(
                condition=Q(received_quantity__lte=F("quantity")),
                name="exchanges_received_lte_qty",
            ),
            models.CheckConstraint(
                condition=Q(accepted_quantity__lte=F("received_quantity")),
                name="exchanges_accepted_lte_received",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.exchange_id}: {self.order_item.sku} -> {self.target_variant.sku}"


class ExchangeReservation(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Đang giữ"
        CAPTURED = "captured", "Đã xuất đổi"
        RELEASED = "released", "Đã hoàn giữ"

    exchange_item = models.OneToOneField(
        ExchangeItem, on_delete=models.PROTECT, related_name="reservation"
    )
    variant = models.ForeignKey(
        "catalog.ProductVariant", on_delete=models.PROTECT, related_name="exchange_reservations"
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
                condition=Q(quantity__gt=0), name="exchanges_reservation_qty_gt_0"
            )
        ]

    def __str__(self) -> str:
        return f"Exchange item {self.exchange_item_id}: {self.status}"


class ExchangeStatusHistory(models.Model):
    exchange = models.ForeignKey(
        ExchangeRequest, on_delete=models.PROTECT, related_name="status_history"
    )
    from_status = models.CharField(
        max_length=24, choices=ExchangeRequest.Status.choices, blank=True
    )
    to_status = models.CharField(max_length=24, choices=ExchangeRequest.Status.choices)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="exchange_status_changes",
    )
    note = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]

    def __str__(self) -> str:
        return f"Exchange {self.exchange_id}: {self.from_status} -> {self.to_status}"
