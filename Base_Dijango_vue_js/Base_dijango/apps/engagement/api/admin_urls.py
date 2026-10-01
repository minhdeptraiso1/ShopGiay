from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminReviewListView,
    AdminReviewModerateView,
    BannerAdminViewSet,
    VoucherAdminViewSet,
)

router = DefaultRouter()
router.register("vouchers", VoucherAdminViewSet, basename="admin-voucher")
router.register("banners", BannerAdminViewSet, basename="admin-banner")

urlpatterns = [
    path("", include(router.urls)),
    path("reviews/", AdminReviewListView.as_view(), name="admin-review-list"),
    path(
        "reviews/<int:review_id>/moderate/",
        AdminReviewModerateView.as_view(),
        name="admin-review-moderate",
    ),
]
