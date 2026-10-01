from rest_framework import serializers

from apps.catalog.api.serializers import ProductImageSerializer
from apps.catalog.models import ProductVariant
from apps.orders.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    OrderStatusHistory,
    Payment,
    PaymentAttempt,
)
from apps.orders.services import CheckoutQuote


class AddCartItemInputSerializer(serializers.Serializer):
    variant = serializers.PrimaryKeyRelatedField(queryset=ProductVariant.objects.all())
    quantity = serializers.IntegerField(min_value=1, max_value=99)
    recommendation_context_id = serializers.UUIDField(required=False, allow_null=True)


class UpdateCartItemInputSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, max_value=99)


class CartVariantOutputSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.name")
    product_slug = serializers.CharField(source="product.slug")
    brand_name = serializers.CharField(source="product.brand.name")
    size_label = serializers.CharField(source="size.label", allow_null=True)
    color_name = serializers.CharField(source="color.name", allow_null=True)
    inventory_quantity = serializers.SerializerMethodField()
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariant
        fields = (
            "id",
            "sku",
            "product_name",
            "product_slug",
            "brand_name",
            "size_label",
            "color_name",
            "option_label",
            "price",
            "currency",
            "inventory_quantity",
            "primary_image",
            "is_active",
        )

    def get_inventory_quantity(self, obj: ProductVariant) -> int:
        inventory = getattr(obj, "inventory", None)
        return inventory.quantity if inventory else 0

    def get_primary_image(self, obj: ProductVariant) -> dict | None:
        images = list(obj.product.images.all())
        image = next((item for item in images if item.is_primary), images[0] if images else None)
        return ProductImageSerializer(image, context=self.context).data if image else None


class CartItemOutputSerializer(serializers.ModelSerializer):
    variant = CartVariantOutputSerializer(read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ("id", "variant", "quantity", "line_total", "created_at", "updated_at")

    def get_line_total(self, obj: CartItem) -> str:
        return str(obj.variant.price * obj.quantity)


class CartOutputSerializer(serializers.ModelSerializer):
    items = CartItemOutputSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ("id", "items", "item_count", "subtotal", "currency", "updated_at")

    def get_item_count(self, obj: Cart) -> int:
        return sum(item.quantity for item in obj.items.all())

    def get_subtotal(self, obj: Cart) -> str:
        return str(sum(item.variant.price * item.quantity for item in obj.items.all()))

    def get_currency(self, obj: Cart) -> str:
        return "VND"


class CheckoutInputSerializer(serializers.Serializer):
    address_id = serializers.IntegerField(min_value=1)
    cart_item_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1), allow_empty=False, max_length=100
    )
    voucher_code = serializers.CharField(
        required=False, allow_blank=True, max_length=32, default=""
    )

    def validate_cart_item_ids(self, value: list[int]) -> list[int]:
        if len(value) != len(set(value)):
            raise serializers.ValidationError("cart_item_ids không được trùng nhau.")
        return value


class CreateOrderInputSerializer(CheckoutInputSerializer):
    payment_method = serializers.ChoiceField(
        choices=Order.PaymentMethod.choices, default=Order.PaymentMethod.COD
    )


class QuoteLineSerializer(serializers.Serializer):
    cart_item_id = serializers.IntegerField()
    variant_id = serializers.IntegerField()
    sku = serializers.CharField()
    product_name = serializers.CharField()
    size_label = serializers.CharField()
    color_name = serializers.CharField()
    quantity = serializers.IntegerField()
    unit_price = serializers.DecimalField(max_digits=14, decimal_places=0)
    discount_total = serializers.DecimalField(max_digits=14, decimal_places=0)
    line_total = serializers.DecimalField(max_digits=14, decimal_places=0)
    currency = serializers.CharField()


class CheckoutQuoteOutputSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    lines = QuoteLineSerializer(many=True)
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=0)
    shipping_fee = serializers.DecimalField(max_digits=14, decimal_places=0)
    discount_total = serializers.DecimalField(max_digits=14, decimal_places=0)
    total = serializers.DecimalField(max_digits=14, decimal_places=0)
    currency = serializers.CharField()
    voucher_code = serializers.CharField()


class OrderItemOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "variant",
            "quantity",
            "product_name",
            "product_slug",
            "sku",
            "size_label",
            "color_name",
            "unit_price",
            "discount_total",
            "line_total",
            "currency",
        )


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True, allow_null=True)

    class Meta:
        model = OrderStatusHistory
        fields = ("id", "from_status", "to_status", "actor", "actor_email", "note", "created_at")


class OrderOutputSerializer(serializers.ModelSerializer):
    items = OrderItemOutputSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    voucher_code = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            "id",
            "number",
            "status",
            "payment_method",
            "payment_status",
            "currency",
            "subtotal",
            "shipping_fee",
            "discount_total",
            "voucher_code",
            "total",
            "recipient_name",
            "phone_number",
            "province",
            "district",
            "ward",
            "street_address",
            "items",
            "status_history",
            "created_at",
            "updated_at",
            "cancelled_at",
        )

    def get_voucher_code(self, obj: Order) -> str:
        try:
            return obj.voucher_usage.voucher.code
        except AttributeError:
            return ""


class PaginatedOrderOutputSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = OrderOutputSerializer(many=True)


class CreatePaymentInputSerializer(serializers.Serializer):
    locale = serializers.ChoiceField(choices=("vn", "en"), default="vn", required=False)
    bank_code = serializers.RegexField(
        regex=r"^[A-Za-z0-9]*$", max_length=20, allow_blank=True, default="", required=False
    )
    return_url = serializers.URLField(max_length=500, allow_blank=True, default="", required=False)


class PaymentAttemptOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentAttempt
        fields = ("id", "reference", "status", "checkout_url", "expires_at", "created_at")


class PaymentOutputSerializer(serializers.ModelSerializer):
    attempts = PaymentAttemptOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "provider",
            "status",
            "amount",
            "currency",
            "provider_transaction_no",
            "paid_at",
            "attempts",
            "created_at",
            "updated_at",
        )


class VnpayIpnOutputSerializer(serializers.Serializer):
    RspCode = serializers.CharField()
    Message = serializers.CharField()


class VnpayReturnInputSerializer(serializers.Serializer):
    params = serializers.DictField(child=serializers.CharField(max_length=1000), allow_empty=False)


class VnpayReturnOutputSerializer(serializers.Serializer):
    response_code = serializers.CharField()
    message = serializers.CharField()
    order_status = serializers.CharField()
    payment_status = serializers.CharField()


def serialize_quote(quote: CheckoutQuote) -> dict:
    return CheckoutQuoteOutputSerializer(quote).data
