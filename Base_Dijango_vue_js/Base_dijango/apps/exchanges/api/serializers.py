from rest_framework import serializers

from ..models import ExchangeItem, ExchangeRequest, ExchangeStatusHistory


class ExchangeCreateItemSerializer(serializers.Serializer):
    order_item_id = serializers.IntegerField(min_value=1)
    target_variant_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class ExchangeCreateInputSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(min_length=3, max_length=500)
    evidence_url = serializers.URLField(
        max_length=500, required=False, allow_blank=True, default=""
    )
    customer_note = serializers.CharField(
        max_length=1000, required=False, allow_blank=True, default=""
    )
    items = ExchangeCreateItemSerializer(many=True, allow_empty=False, max_length=50)

    def validate_items(self, value: list[dict]) -> list[dict]:
        ids = [item["order_item_id"] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Mỗi sản phẩm đơn hàng chỉ được xuất hiện một lần.")
        return value


class ExchangeItemOutputSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="order_item.product_name", read_only=True)
    product_slug = serializers.CharField(source="order_item.product_slug", read_only=True)
    source_variant_id = serializers.IntegerField(source="order_item.variant_id", read_only=True)
    source_sku = serializers.CharField(source="order_item.sku", read_only=True)
    source_size = serializers.CharField(source="order_item.size_label", read_only=True)
    source_color = serializers.CharField(source="order_item.color_name", read_only=True)
    target_sku = serializers.CharField(source="target_variant.sku", read_only=True)
    target_size = serializers.CharField(
        source="target_variant.size.label", read_only=True, allow_null=True
    )
    target_color = serializers.CharField(
        source="target_variant.color.name", read_only=True, allow_null=True
    )

    class Meta:
        model = ExchangeItem
        fields = (
            "id",
            "order_item",
            "product_name",
            "product_slug",
            "source_variant_id",
            "source_sku",
            "source_size",
            "source_color",
            "target_variant",
            "target_sku",
            "target_size",
            "target_color",
            "quantity",
            "received_quantity",
            "accepted_quantity",
            "disposition",
            "inspection_note",
        )


class ExchangeHistorySerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True, allow_null=True)

    class Meta:
        model = ExchangeStatusHistory
        fields = ("id", "from_status", "to_status", "actor_email", "note", "created_at")


class ExchangeOutputSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source="order.number", read_only=True)
    customer_email = serializers.EmailField(source="user.email", read_only=True)
    approved_by_email = serializers.EmailField(
        source="approved_by.email", read_only=True, allow_null=True
    )
    items = ExchangeItemOutputSerializer(many=True, read_only=True)
    status_history = ExchangeHistorySerializer(many=True, read_only=True)

    class Meta:
        model = ExchangeRequest
        fields = (
            "id",
            "order",
            "order_number",
            "customer_email",
            "status",
            "reason",
            "evidence_url",
            "customer_note",
            "staff_note",
            "tracking_number",
            "approved_by_email",
            "reservation_expires_at",
            "items",
            "status_history",
            "created_at",
            "updated_at",
        )


class ExchangeReceiveItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(min_value=1)
    received_quantity = serializers.IntegerField(min_value=0)


class ExchangeInspectItemSerializer(serializers.Serializer):
    item_id = serializers.IntegerField(min_value=1)
    accepted_quantity = serializers.IntegerField(min_value=0)
    disposition = serializers.ChoiceField(choices=ExchangeItem.Disposition.choices)
    inspection_note = serializers.CharField(
        max_length=500, required=False, allow_blank=True, default=""
    )


class ExchangeTransitionInputSerializer(serializers.Serializer):
    action = serializers.ChoiceField(
        choices=("approve", "reject", "receive", "inspect", "prepare", "ship")
    )
    expected_updated_at = serializers.DateTimeField()
    note = serializers.CharField(max_length=1000, required=False, allow_blank=True, default="")
    tracking_number = serializers.CharField(
        max_length=100, required=False, allow_blank=True, default=""
    )
    received_items = ExchangeReceiveItemSerializer(many=True, required=False, default=list)
    inspected_items = ExchangeInspectItemSerializer(many=True, required=False, default=list)

    def validate(self, attrs):
        action = attrs["action"]
        if action == "receive" and not attrs["received_items"]:
            raise serializers.ValidationError({"received_items": "Cần nhập số lượng thực nhận."})
        if action == "inspect" and not attrs["inspected_items"]:
            raise serializers.ValidationError({"inspected_items": "Cần nhập kết quả kiểm hàng."})
        if action == "ship" and not attrs["tracking_number"].strip():
            raise serializers.ValidationError({"tracking_number": "Cần nhập mã vận đơn."})
        return attrs
