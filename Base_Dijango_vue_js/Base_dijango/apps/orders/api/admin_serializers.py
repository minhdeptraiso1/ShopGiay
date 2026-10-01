from rest_framework import serializers

from apps.orders.models import Order

from .serializers import OrderOutputSerializer


class AdminOrderOutputSerializer(OrderOutputSerializer):
    customer_email = serializers.EmailField(source="user.email", read_only=True)

    class Meta(OrderOutputSerializer.Meta):
        fields = OrderOutputSerializer.Meta.fields + ("customer_email",)


class OrderTransitionInputSerializer(serializers.Serializer):
    to_status = serializers.ChoiceField(choices=Order.Status.choices)
    expected_updated_at = serializers.DateTimeField()
    note = serializers.CharField(max_length=255, allow_blank=True, required=False, default="")


class PaginatedAdminOrderOutputSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = AdminOrderOutputSerializer(many=True)
