import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db import models
from django.db.models import F, Q


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="children"
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({"parent": "Danh mục không thể là cha của chính nó."})


class Brand(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Nháp"
        PUBLISHED = "published", "Đang bán"
        INACTIVE = "inactive", "Ngừng hoạt động"

    class ProductType(models.TextChoices):
        FOOTWEAR = "footwear", "Giày dép"
        ACCESSORY = "accessory", "Phụ kiện"
        CARE = "care", "Chăm sóc giày"

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    product_type = models.CharField(
        max_length=16, choices=ProductType.choices, default=ProductType.FOOTWEAR, db_index=True
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["brand", "category", "status"])]

    def __str__(self) -> str:
        return self.name


class Size(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="sizes")
    label = models.CharField(max_length=40)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["brand__name", "sort_order", "label"]
        constraints = [
            models.UniqueConstraint(fields=["brand", "label"], name="catalog_size_brand_label_uniq")
        ]

    def __str__(self) -> str:
        return f"{self.brand.name} {self.label}"


class Color(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    hex_code = models.CharField(max_length=7, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.FileField(
        upload_to="products/%Y/%m/",
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
        blank=True,
    )
    external_url = models.URLField(max_length=500, blank=True)
    alt_text = models.CharField(max_length=180, blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["product"],
                condition=Q(is_primary=True),
                name="catalog_one_primary_image_per_product",
            )
        ]

    def __str__(self) -> str:
        return f"{self.product.name} - {self.image.name or self.external_url}"

    def clean(self) -> None:
        if bool(self.image) == bool(self.external_url):
            raise ValidationError("Ảnh sản phẩm phải có đúng một nguồn: file hoặc URL bên ngoài.")


class ProductVariant(models.Model):
    class Currency(models.TextChoices):
        VND = "VND", "Vietnamese đồng"

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="variants")
    size = models.ForeignKey(
        Size, null=True, blank=True, on_delete=models.PROTECT, related_name="variants"
    )
    color = models.ForeignKey(
        Color, null=True, blank=True, on_delete=models.PROTECT, related_name="variants"
    )
    option_label = models.CharField(max_length=80, blank=True)
    sku = models.CharField(max_length=64, unique=True)
    price = models.DecimalField(max_digits=14, decimal_places=0, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.VND)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["product_id", "size__sort_order", "color__name"]
        constraints = [
            models.CheckConstraint(condition=Q(price__gte=0), name="catalog_variant_price_gte_0"),
            models.CheckConstraint(
                condition=Q(currency="VND"), name="catalog_variant_currency_vnd"
            ),
        ]
        indexes = [models.Index(fields=["product", "is_active"])]

    def __str__(self) -> str:
        return self.sku

    def clean(self) -> None:
        if self.product_id and self.size_id and self.product.brand_id != self.size.brand_id:
            raise ValidationError({"size": "Size phải thuộc cùng thương hiệu với sản phẩm."})


class InventoryBalance(models.Model):
    variant = models.OneToOneField(
        ProductVariant, on_delete=models.PROTECT, related_name="inventory"
    )
    quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(quantity__gte=0), name="catalog_inventory_qty_gte_0")
        ]

    def __str__(self) -> str:
        return f"{self.variant.sku}: {self.quantity}"


class StockMovement(models.Model):
    class Kind(models.TextChoices):
        RECEIPT = "receipt", "Nhập kho"
        ADJUSTMENT = "adjustment", "Điều chỉnh"
        SALE = "sale", "Bán hàng"
        CANCELLATION = "cancellation", "Hoàn do hủy đơn"
        RESERVATION = "reservation", "Giữ hàng thanh toán online"
        RESERVATION_RELEASE = "reservation_release", "Hoàn giữ hàng hết hạn/hủy"
        EXCHANGE_RESERVATION = "exchange_reservation", "Giữ hàng đổi"
        EXCHANGE_RELEASE = "exchange_release", "Hoàn giữ hàng đổi"
        EXCHANGE_RETURN = "exchange_return", "Nhập lại hàng đổi"

    variant = models.ForeignKey(
        ProductVariant, on_delete=models.PROTECT, related_name="stock_movements"
    )
    kind = models.CharField(max_length=20, choices=Kind.choices)
    delta = models.IntegerField()
    quantity_before = models.PositiveIntegerField()
    quantity_after = models.PositiveIntegerField()
    reason = models.CharField(max_length=255)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="stock_movements",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.CheckConstraint(condition=~Q(delta=0), name="catalog_stock_delta_nonzero"),
            models.CheckConstraint(
                condition=Q(quantity_after=F("quantity_before") + F("delta")),
                name="catalog_stock_after_matches_delta",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.variant.sku}: {self.delta:+d}"

    def save(self, *args, **kwargs) -> None:
        if self.pk:
            raise ValidationError("Stock movement là lịch sử bất biến và không thể sửa.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Stock movement là lịch sử bất biến và không thể xóa.")


class ProductEvent(models.Model):
    class EventType(models.TextChoices):
        VIEW = "view", "Xem sản phẩm"
        ADD_CART = "add_cart", "Thêm giỏ hàng"
        RECOMMENDATION_IMPRESSION = "recommendation_impression", "Hiển thị gợi ý"
        RECOMMENDATION_CLICK = "recommendation_click", "Nhấp gợi ý"
        WISHLIST_ADD = "wishlist_add", "Thêm yêu thích"
        WISHLIST_REMOVE = "wishlist_remove", "Bỏ yêu thích"
        PURCHASE = "purchase", "Mua hàng hoàn tất"

    class Source(models.TextChoices):
        STOREFRONT = "storefront", "Cửa hàng"
        SEARCH = "search", "Tìm kiếm"
        RECOMMENDATION = "recommendation", "Gợi ý"

    client_event_id = models.UUIDField(unique=True)
    schema_version = models.PositiveSmallIntegerField(default=1)
    event_type = models.CharField(max_length=40, choices=EventType.choices, db_index=True)
    source = models.CharField(max_length=24, choices=Source.choices)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="events")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="product_events",
    )
    anonymous_id = models.UUIDField(null=True, blank=True, db_index=True)
    recommendation_context_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["product", "event_type", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.event_type}:{self.product_id}"


class RecommendationRequest(models.Model):
    class Strategy(models.TextChoices):
        POPULAR = "popular", "Phổ biến"
        SIMILAR = "similar", "Tương tự"
        PERSONALIZED = "personalized", "Cá nhân hóa"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    strategy = models.CharField(max_length=20, choices=Strategy.choices, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="recommendation_requests",
    )
    anonymous_id = models.UUIDField(null=True, blank=True, db_index=True)
    source_product = models.ForeignKey(
        Product,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="similar_recommendation_requests",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.strategy}:{self.id}"


class RecommendationItem(models.Model):
    request = models.ForeignKey(
        RecommendationRequest, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="recommendation_items"
    )
    rank = models.PositiveSmallIntegerField()
    score = models.DecimalField(max_digits=12, decimal_places=4, default=0)

    class Meta:
        ordering = ["rank"]
        constraints = [
            models.UniqueConstraint(
                fields=["request", "product"], name="catalog_recommendation_product_uniq"
            ),
            models.UniqueConstraint(
                fields=["request", "rank"], name="catalog_recommendation_rank_uniq"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.request_id} #{self.rank}: {self.product_id}"
