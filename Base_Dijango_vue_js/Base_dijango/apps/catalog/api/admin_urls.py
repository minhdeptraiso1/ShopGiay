from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .admin_views import (
    BrandAdminViewSet,
    CategoryAdminViewSet,
    ColorAdminViewSet,
    InventoryAdjustmentView,
    ProductAdminViewSet,
    ProductImageAdminViewSet,
    ProductVariantAdminViewSet,
    RecommendationMetricsView,
    SizeAdminViewSet,
    StockMovementListView,
)

router = DefaultRouter()
router.register("categories", CategoryAdminViewSet, basename="admin-category")
router.register("brands", BrandAdminViewSet, basename="admin-brand")
router.register("products", ProductAdminViewSet, basename="admin-product")
router.register("sizes", SizeAdminViewSet, basename="admin-size")
router.register("colors", ColorAdminViewSet, basename="admin-color")
router.register("variants", ProductVariantAdminViewSet, basename="admin-variant")
router.register("product-images", ProductImageAdminViewSet, basename="admin-product-image")

urlpatterns = [
    path(
        "recommendations/metrics/",
        RecommendationMetricsView.as_view(),
        name="recommendation-metrics",
    ),
    path("", include(router.urls)),
    path(
        "inventory/variants/<int:variant_id>/adjustments/",
        InventoryAdjustmentView.as_view(),
        name="inventory-adjustment",
    ),
    path(
        "inventory/variants/<int:variant_id>/movements/",
        StockMovementListView.as_view(),
        name="stock-movement-list",
    ),
]
