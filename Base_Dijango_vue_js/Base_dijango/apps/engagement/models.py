from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class Voucher(models.Model):
    class DiscountType(models.TextChoices):
        PERCENT = "percent", "Phần trăm"
        FIXED = "fixed", "Số tiền cố định"

    code = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=160)
    discount_type = models.CharField(max_length=12, choices=DiscountType.choices)
    value = models.DecimalField(max_digits=14, decimal_places=0, validators=[MinValueValidator(1)])
    max_discount = models.DecimalField(
        max_digits=14, decimal_places=0, null=True, blank=True, validators=[MinValueValidator(1)]
    )
    min_order_value = models.DecimalField(max_digits=14, decimal_places=0, default=0)
    required_points = models.PositiveIntegerField(default=0)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(null=True, blank=True)
    per_user_limit = models.PositiveIntegerField(default=1)
    products = models.ManyToManyField("catalog.Product", blank=True, related_name="vouchers")
    categories = models.ManyToManyField("catalog.Category", blank=True, related_name="vouchers")
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "code"]
        constraints = [
            models.CheckConstraint(condition=Q(value__gt=0), name="engagement_voucher_value_gt_0"),
            models.CheckConstraint(
                condition=Q(min_order_value__gte=0), name="engagement_voucher_min_order_gte_0"
            ),
            models.CheckConstraint(
                condition=Q(ends_at__gt=models.F("starts_at")),
                name="engagement_voucher_window_valid",
            ),
        ]

    def __str__(self) -> str:
        return self.code

    def save(self, *args, **kwargs) -> None:
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)


class VoucherUsage(models.Model):
    class Status(models.TextChoices):
        RESERVED = "reserved", "Đang giữ"
        REDEEMED = "redeemed", "Đã dùng"
        RELEASED = "released", "Đã hoàn"

    voucher = models.ForeignKey(Voucher, on_delete=models.PROTECT, related_name="usages")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="voucher_usages"
    )
    order = models.OneToOneField(
        "orders.Order", on_delete=models.PROTECT, related_name="voucher_usage"
    )
    status = models.CharField(max_length=12, choices=Status.choices)
    discount_amount = models.DecimalField(max_digits=14, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=Q(discount_amount__gte=0), name="engagement_usage_discount_gte_0"
            )
        ]

    def __str__(self) -> str:
        return f"{self.voucher.code} - order {self.order_id}"


class VoucherAllocation(models.Model):
    usage = models.ForeignKey(VoucherUsage, on_delete=models.PROTECT, related_name="allocations")
    order_item = models.OneToOneField(
        "orders.OrderItem", on_delete=models.PROTECT, related_name="voucher_allocation"
    )
    amount = models.DecimalField(max_digits=14, decimal_places=0)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gte=0), name="engagement_allocation_amount_gte_0"
            )
        ]

    def __str__(self) -> str:
        return f"Usage {self.usage_id} - item {self.order_item_id}"


class WishlistItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist_items"
    )
    product = models.ForeignKey(
        "catalog.Product", on_delete=models.CASCADE, related_name="wishlists"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"], name="engagement_wishlist_user_product_uniq"
            )
        ]

    def __str__(self) -> str:
        return f"User {self.user_id} - product {self.product_id}"


class Review(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Chờ duyệt"
        APPROVED = "approved", "Đã duyệt"
        REJECTED = "rejected", "Từ chối"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reviews"
    )
    product = models.ForeignKey("catalog.Product", on_delete=models.PROTECT, related_name="reviews")
    order_item = models.OneToOneField(
        "orders.OrderItem", on_delete=models.PROTECT, related_name="review"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    content = models.TextField(max_length=2000)
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.PENDING, db_index=True
    )
    moderation_note = models.CharField(max_length=500, blank=True)
    moderated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="moderated_reviews",
    )
    moderated_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["product", "status", "-created_at"])]
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__gte=1) & Q(rating__lte=5),
                name="engagement_review_rating_1_5",
            )
        ]

    def __str__(self) -> str:
        return f"Review {self.id} - {self.rating}/5"


class Banner(models.Model):
    class Position(models.TextChoices):
        HOME_HERO = "home_hero", "Hero trang chủ"
        HOME_STRIP = "home_strip", "Dải trang chủ"
        PRODUCTS_TOP = "products_top", "Đầu trang sản phẩm"

    title = models.CharField(max_length=180)
    subtitle = models.CharField(max_length=300, blank=True)
    image_url = models.URLField(max_length=500)
    target_url = models.CharField(max_length=500, blank=True)
    position = models.CharField(max_length=24, choices=Position.choices, db_index=True)
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["position", "sort_order", "id"]
        constraints = [
            models.CheckConstraint(
                condition=Q(ends_at__gt=models.F("starts_at")),
                name="engagement_banner_window_valid",
            )
        ]

    def __str__(self) -> str:
        return self.title
