from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    PersonalizedRecommendationView,
    PopularRecommendationView,
    ProductEventView,
    PublicBrandViewSet,
    PublicCategoryViewSet,
    PublicColorViewSet,
    PublicProductViewSet,
    PublicSizeViewSet,
    SimilarRecommendationView,
)

router = DefaultRouter()
router.register("categories", PublicCategoryViewSet, basename="public-category")
router.register("brands", PublicBrandViewSet, basename="public-brand")
router.register("sizes", PublicSizeViewSet, basename="public-size")
router.register("colors", PublicColorViewSet, basename="public-color")
router.register("products", PublicProductViewSet, basename="public-product")

urlpatterns = [
    path("events/", ProductEventView.as_view(), name="event"),
    path(
        "recommendations/popular/",
        PopularRecommendationView.as_view(),
        name="recommendations-popular",
    ),
    path(
        "recommendations/personalized/",
        PersonalizedRecommendationView.as_view(),
        name="recommendations-personalized",
    ),
    path(
        "products/<int:product_id>/recommendations/",
        SimilarRecommendationView.as_view(),
        name="recommendations-similar",
    ),
    path("", include(router.urls)),
]
