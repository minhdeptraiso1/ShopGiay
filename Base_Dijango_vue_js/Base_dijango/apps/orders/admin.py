from django.contrib import admin

from .models import (
    Cart,
    CartItem,
    InventoryReservation,
    Order,
    OrderItem,
    OrderStatusHistory,
    Payment,
    PaymentAttempt,
    PaymentEvent,
)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ("variant", "quantity", "created_at", "updated_at")


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "updated_at")
    inlines = (CartItemInline,)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        "variant",
        "quantity",
        "product_name",
        "sku",
        "size_label",
        "color_name",
        "unit_price",
        "discount_total",
        "line_total",
    )


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ("from_status", "to_status", "actor", "note", "created_at")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("number", "user", "status", "payment_status", "total", "created_at")
    list_filter = ("status", "payment_status", "payment_method")
    search_fields = ("number", "user__email", "phone_number")
    readonly_fields = (
        "number",
        "user",
        "address",
        "idempotency_key",
        "request_fingerprint",
        "subtotal",
        "shipping_fee",
        "discount_total",
        "total",
        "recipient_name",
        "phone_number",
        "province",
        "district",
        "ward",
        "street_address",
        "created_at",
        "updated_at",
        "cancelled_at",
    )
    inlines = (OrderItemInline, OrderStatusHistoryInline)

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


admin.site.register(Payment)
admin.site.register(PaymentAttempt)
admin.site.register(PaymentEvent)
admin.site.register(InventoryReservation)
