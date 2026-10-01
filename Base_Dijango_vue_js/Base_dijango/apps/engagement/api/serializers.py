from rest_framework import serializers

from apps.catalog.api.serializers import ProductListSerializer
from apps.catalog.models import Category, Product

from ..models import Banner, Review, Voucher, WishlistItem


class VoucherAdminSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), many=True, required=False
    )
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )
    usage_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Voucher
        fields = (
            "id",
            "code",
            "name",
            "discount_type",
            "value",
            "max_discount",
            "min_order_value",
            "required_points",
            "starts_at",
            "ends_at",
            "usage_limit",
            "per_user_limit",
            "products",
            "categories",
            "is_active",
            "usage_count",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "usage_count", "created_at", "updated_at")

    def validate(self, attrs):
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))
        discount_type = attrs.get("discount_type", getattr(self.instance, "discount_type", None))
        value = attrs.get("value", getattr(self.instance, "value", None))
        if starts_at and ends_at and starts_at >= ends_at:
            raise serializers.ValidationError({"ends_at": "Thời gian kết thúc phải sau bắt đầu."})
        if discount_type == Voucher.DiscountType.PERCENT and value and value > 100:
            raise serializers.ValidationError(
                {"value": "Voucher phần trăm không được vượt quá 100%."}
            )
        return attrs

    def validate_code(self, value: str) -> str:
        return value.strip().upper()


class VoucherValidateInputSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=32)
    address_id = serializers.IntegerField(min_value=1)
    cart_item_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=False, max_length=100
    )


class VoucherValidationOutputSerializer(serializers.Serializer):
    code = serializers.CharField()
    discount_total = serializers.DecimalField(max_digits=14, decimal_places=0)
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=0)
    total = serializers.DecimalField(max_digits=14, decimal_places=0)
    currency = serializers.CharField()


class EligibleVoucherSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    code = serializers.CharField()
    name = serializers.CharField()
    discount_type = serializers.CharField()
    value = serializers.DecimalField(max_digits=14, decimal_places=0)
    max_discount = serializers.DecimalField(max_digits=14, decimal_places=0, allow_null=True)
    min_order_value = serializers.DecimalField(max_digits=14, decimal_places=0)
    required_points = serializers.IntegerField()
    discount_total = serializers.DecimalField(max_digits=14, decimal_places=0)
    total = serializers.DecimalField(max_digits=14, decimal_places=0)


class EligibleVoucherOutputSerializer(serializers.Serializer):
    points_balance = serializers.IntegerField()
    vouchers = EligibleVoucherSerializer(many=True)


class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)

    class Meta:
        model = WishlistItem
        fields = ("id", "product", "created_at")


class WishlistToggleInputSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(status=Product.Status.PUBLISHED)
    )


class WishlistToggleOutputSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    is_wishlisted = serializers.BooleanField()


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    product_name = serializers.CharField(source="product.name", read_only=True)
    moderator_email = serializers.EmailField(
        source="moderated_by.email", read_only=True, allow_null=True
    )

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "user_name",
            "product",
            "product_name",
            "order_item",
            "rating",
            "content",
            "status",
            "moderation_note",
            "moderated_by",
            "moderator_email",
            "moderated_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_user_name(self, obj: Review) -> str:
        return obj.user.full_name or "Khách hàng đã mua"


class ReviewCreateInputSerializer(serializers.Serializer):
    order_item = serializers.IntegerField(min_value=1)
    rating = serializers.IntegerField(min_value=1, max_value=5)
    content = serializers.CharField(min_length=10, max_length=2000)


class ReviewUpdateInputSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)
    content = serializers.CharField(min_length=10, max_length=2000)


class ReviewModerateInputSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=(Review.Status.APPROVED, Review.Status.REJECTED))
    moderation_note = serializers.CharField(max_length=500, allow_blank=True, required=False)


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = (
            "id",
            "title",
            "subtitle",
            "image_url",
            "target_url",
            "position",
            "starts_at",
            "ends_at",
            "sort_order",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def validate(self, attrs):
        starts_at = attrs.get("starts_at", getattr(self.instance, "starts_at", None))
        ends_at = attrs.get("ends_at", getattr(self.instance, "ends_at", None))
        if starts_at and ends_at and starts_at >= ends_at:
            raise serializers.ValidationError({"ends_at": "Thời gian kết thúc phải sau bắt đầu."})
        return attrs
