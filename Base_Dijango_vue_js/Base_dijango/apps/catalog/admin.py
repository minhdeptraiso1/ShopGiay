from django.contrib import admin

from .models import (
    Brand,
    Category,
    Color,
    InventoryBalance,
    Product,
    ProductEvent,
    ProductImage,
    ProductVariant,
    RecommendationItem,
    RecommendationRequest,
    Size,
    StockMovement,
)


@admin.register(Category, Brand, Color, Size)
class CatalogReferenceAdmin(admin.ModelAdmin):
    list_display = ("id", "__str__", "is_active")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "product_type", "brand", "category", "status", "updated_at")
    list_filter = ("status", "product_type", "brand", "category")
    search_fields = ("name", "slug", "variants__sku")


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "sku",
        "product",
        "size",
        "color",
        "option_label",
        "price",
        "is_active",
    )
    search_fields = ("sku", "product__name")


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "is_primary", "sort_order")


@admin.register(InventoryBalance)
class InventoryBalanceAdmin(admin.ModelAdmin):
    list_display = ("variant", "quantity", "updated_at")
    readonly_fields = ("variant", "quantity", "updated_at")

    def has_add_permission(self, request) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("id", "variant", "kind", "delta", "quantity_after", "actor", "created_at")
    readonly_fields = (
        "variant",
        "kind",
        "delta",
        "quantity_before",
        "quantity_after",
        "reason",
        "actor",
        "created_at",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


@admin.register(ProductEvent)
class ProductEventAdmin(admin.ModelAdmin):
    list_display = ("id", "event_type", "product", "user", "source", "created_at")
    readonly_fields = (
        "client_event_id",
        "schema_version",
        "event_type",
        "source",
        "product",
        "user",
        "anonymous_id",
        "recommendation_context_id",
        "created_at",
    )

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False


class RecommendationItemInline(admin.TabularInline):
    model = RecommendationItem
    extra = 0
    readonly_fields = ("product", "rank", "score")


@admin.register(RecommendationRequest)
class RecommendationRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "strategy", "user", "source_product", "created_at")
    list_filter = ("strategy",)
    readonly_fields = ("id", "strategy", "user", "anonymous_id", "source_product", "created_at")
    inlines = (RecommendationItemInline,)

    def has_add_permission(self, request) -> bool:
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        return False
