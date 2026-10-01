from django.core.validators import RegexValidator
from rest_framework import serializers

from apps.catalog.models import (
    Brand,
    Category,
    Color,
    Product,
    ProductEvent,
    ProductImage,
    ProductVariant,
    RecommendationItem,
    Size,
    StockMovement,
)


class ProductFilterSerializer(serializers.Serializer):
    search = serializers.CharField(required=False, allow_blank=True, max_length=120)
    category = serializers.SlugField(required=False, allow_blank=True)
    brand = serializers.SlugField(required=False, allow_blank=True)
    size = serializers.CharField(required=False, allow_blank=True, max_length=40)
    color = serializers.SlugField(required=False, allow_blank=True)
    min_price = serializers.DecimalField(
        required=False, max_digits=14, decimal_places=0, min_value=0
    )
    max_price = serializers.DecimalField(
        required=False, max_digits=14, decimal_places=0, min_value=0
    )
    in_stock = serializers.BooleanField(required=False, allow_null=True, default=None)
    ordering = serializers.ChoiceField(
        required=False, choices=("newest", "name", "-name", "price", "-price")
    )

    def validate(self, attrs):
        min_price = attrs.get("min_price")
        max_price = attrs.get("max_price")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise serializers.ValidationError(
                {"max_price": "Giá tối đa phải lớn hơn hoặc bằng giá tối thiểu."}
            )
        return attrs


class SizeFilterSerializer(serializers.Serializer):
    brand = serializers.SlugField(required=False, allow_blank=True)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "parent",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ("id", "name", "slug", "description", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class SizeSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source="brand.name", read_only=True)

    class Meta:
        model = Size
        fields = ("id", "brand", "brand_name", "label", "sort_order", "is_active")
        read_only_fields = ("id", "brand_name")


class ColorSerializer(serializers.ModelSerializer):
    hex_code = serializers.CharField(
        allow_blank=True,
        required=False,
        validators=[RegexValidator(r"^$|^#[0-9A-Fa-f]{6}$", "Mã màu phải có dạng #RRGGBB.")],
    )

    class Meta:
        model = Color
        fields = ("id", "name", "slug", "hex_code", "is_active")
        read_only_fields = ("id",)


class ProductImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = (
            "id",
            "product",
            "image",
            "external_url",
            "image_url",
            "alt_text",
            "sort_order",
            "is_primary",
            "created_at",
        )
        read_only_fields = ("id", "image_url", "created_at")
        extra_kwargs = {
            "image": {"write_only": True, "required": False},
            "external_url": {"write_only": True, "required": False},
        }

    def validate(self, attrs):
        image = attrs.get("image", getattr(self.instance, "image", None))
        external_url = attrs.get("external_url", getattr(self.instance, "external_url", ""))
        if bool(image) == bool(external_url):
            raise serializers.ValidationError(
                "Ảnh sản phẩm phải có đúng một nguồn: file hoặc URL bên ngoài."
            )
        return attrs

    def validate_image(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Ảnh không được lớn hơn 5 MB.")
        content_type = getattr(value, "content_type", "")
        if content_type not in {"image/jpeg", "image/png", "image/webp"}:
            raise serializers.ValidationError("Chỉ chấp nhận JPEG, PNG hoặc WebP.")
        return value

    def get_image_url(self, obj: ProductImage) -> str:
        if obj.external_url:
            return obj.external_url
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


class PublicVariantSerializer(serializers.ModelSerializer):
    size = SizeSerializer(read_only=True)
    color = ColorSerializer(read_only=True)
    inventory_quantity = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "sku",
            "size",
            "color",
            "option_label",
            "price",
            "currency",
            "inventory_quantity",
            "is_available",
        )

    def get_inventory_quantity(self, obj: ProductVariant) -> int:
        inventory = getattr(obj, "inventory", None)
        return inventory.quantity if inventory else 0

    def get_is_available(self, obj: ProductVariant) -> bool:
        return self.get_inventory_quantity(obj) > 0


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    min_price = serializers.SerializerMethodField()
    max_price = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "name",
            "slug",
            "category",
            "brand",
            "product_type",
            "primary_image",
            "min_price",
            "max_price",
            "currency",
            "is_available",
            "published_at",
        )

    def _variants(self, obj: Product) -> list[ProductVariant]:
        return list(getattr(obj, "public_variants", []))

    def get_primary_image(self, obj: Product) -> dict | None:
        images = list(obj.images.all())
        image = next((item for item in images if item.is_primary), images[0] if images else None)
        return ProductImageSerializer(image, context=self.context).data if image else None

    def get_min_price(self, obj: Product) -> str | None:
        prices = [variant.price for variant in self._variants(obj)]
        return str(min(prices)) if prices else None

    def get_max_price(self, obj: Product) -> str | None:
        prices = [variant.price for variant in self._variants(obj)]
        return str(max(prices)) if prices else None

    def get_currency(self, obj: Product) -> str | None:
        variants = self._variants(obj)
        return variants[0].currency if variants else None

    def get_is_available(self, obj: Product) -> bool:
        return any(
            getattr(variant, "inventory", None) and variant.inventory.quantity > 0
            for variant in self._variants(obj)
        )


class ProductDetailSerializer(ProductListSerializer):
    variants = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta(ProductListSerializer.Meta):
        fields = ProductListSerializer.Meta.fields + ("description", "variants", "images")

    def get_variants(self, obj: Product) -> list[dict]:
        return PublicVariantSerializer(self._variants(obj), many=True).data


class ProductAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "category",
            "brand",
            "name",
            "slug",
            "description",
            "product_type",
            "status",
            "published_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "published_at", "created_at", "updated_at")


class ProductVariantAdminSerializer(serializers.ModelSerializer):
    inventory_quantity = serializers.IntegerField(
        source="inventory.quantity", read_only=True, default=0
    )

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "product",
            "size",
            "color",
            "option_label",
            "sku",
            "price",
            "currency",
            "low_stock_threshold",
            "is_active",
            "inventory_quantity",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "inventory_quantity", "created_at", "updated_at")

    def validate(self, attrs):
        instance = self.instance
        product = attrs.get("product", instance.product if instance else None)
        size = attrs.get("size", instance.size if instance else None)
        if product and size and product.brand_id != size.brand_id:
            raise serializers.ValidationError(
                {"size": "Size phải thuộc cùng thương hiệu với sản phẩm."}
            )
        if product and product.product_type == Product.ProductType.FOOTWEAR and not size:
            raise serializers.ValidationError({"size": "Sản phẩm giày cần chọn kích cỡ."})
        return attrs


class InventoryAdjustmentInputSerializer(serializers.Serializer):
    delta = serializers.IntegerField()
    kind = serializers.ChoiceField(choices=StockMovement.Kind.choices)
    reason = serializers.CharField(max_length=255, allow_blank=False, trim_whitespace=True)

    def validate_delta(self, value: int) -> int:
        if value == 0:
            raise serializers.ValidationError("Số lượng điều chỉnh phải khác 0.")
        return value


class StockMovementSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True, allow_null=True)

    class Meta:
        model = StockMovement
        fields = (
            "id",
            "variant",
            "kind",
            "delta",
            "quantity_before",
            "quantity_after",
            "reason",
            "actor",
            "actor_email",
            "created_at",
        )
        read_only_fields = fields


class ProductEventInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductEvent
        fields = (
            "client_event_id",
            "schema_version",
            "event_type",
            "source",
            "product",
            "anonymous_id",
            "recommendation_context_id",
        )
        extra_kwargs = {"client_event_id": {"validators": []}}

    def validate_schema_version(self, value: int) -> int:
        if value != 1:
            raise serializers.ValidationError("Chỉ hỗ trợ schema_version=1.")
        return value

    def validate_product(self, value: Product) -> Product:
        if value.status != Product.Status.PUBLISHED:
            raise serializers.ValidationError("Sản phẩm không khả dụng để ghi nhận sự kiện.")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        if not request.user.is_authenticated and not attrs.get("anonymous_id"):
            raise serializers.ValidationError(
                {"anonymous_id": "Guest phải cung cấp anonymous_id dạng UUID."}
            )
        event_type = attrs.get("event_type")
        client_event_types = {
            ProductEvent.EventType.VIEW,
            ProductEvent.EventType.RECOMMENDATION_IMPRESSION,
            ProductEvent.EventType.RECOMMENDATION_CLICK,
        }
        if event_type not in client_event_types:
            raise serializers.ValidationError(
                {"event_type": "Client không được phép ghi loại sự kiện này."}
            )
        context_id = attrs.get("recommendation_context_id")
        recommendation_events = {
            ProductEvent.EventType.RECOMMENDATION_IMPRESSION,
            ProductEvent.EventType.RECOMMENDATION_CLICK,
        }
        if event_type in recommendation_events and not context_id:
            raise serializers.ValidationError(
                {"recommendation_context_id": "Sự kiện gợi ý phải có context id."}
            )
        if event_type in recommendation_events:
            if attrs.get("source") != ProductEvent.Source.RECOMMENDATION:
                raise serializers.ValidationError(
                    {"source": "Sự kiện gợi ý phải có source=recommendation."}
                )
            if not RecommendationItem.objects.filter(
                request_id=context_id, product=attrs.get("product")
            ).exists():
                raise serializers.ValidationError(
                    {
                        "recommendation_context_id": (
                            "Context không tồn tại hoặc không chứa sản phẩm này."
                        )
                    }
                )
        return attrs


class ProductEventOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductEvent
        fields = ("id", "client_event_id", "created_at")


class RecommendationQuerySerializer(serializers.Serializer):
    anonymous_id = serializers.UUIDField(required=False, allow_null=True)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=12, default=8)


class RecommendationResponseSerializer(serializers.Serializer):
    request_id = serializers.UUIDField()
    strategy = serializers.CharField()
    fallback_used = serializers.BooleanField()
    results = ProductListSerializer(many=True)


class RecommendationMetricsSerializer(serializers.Serializer):
    days = serializers.IntegerField()
    requests = serializers.IntegerField()
    impressions = serializers.IntegerField()
    clicks = serializers.IntegerField()
    attributed_add_to_carts = serializers.IntegerField()
    attributed_purchases = serializers.IntegerField()
    ctr_percent = serializers.DecimalField(max_digits=6, decimal_places=2)
    coverage_percent = serializers.DecimalField(max_digits=6, decimal_places=2)
    requests_by_strategy = serializers.DictField(child=serializers.IntegerField())
