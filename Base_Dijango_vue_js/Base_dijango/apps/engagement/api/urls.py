from django.urls import path

from .views import (
    BannerPublicListView,
    EligibleVoucherListView,
    OwnReviewDetailView,
    ProductReviewListCreateView,
    VoucherValidateView,
    WishlistDetailView,
    WishlistView,
)

urlpatterns = [
    path("banners/", BannerPublicListView.as_view(), name="banner-list"),
    path("vouchers/validate/", VoucherValidateView.as_view(), name="voucher-validate"),
    path("vouchers/eligible/", EligibleVoucherListView.as_view(), name="voucher-eligible"),
    path("wishlist/", WishlistView.as_view(), name="wishlist"),
    path("wishlist/<int:product_id>/", WishlistDetailView.as_view(), name="wishlist-detail"),
    path(
        "products/<int:product_id>/reviews/",
        ProductReviewListCreateView.as_view(),
        name="product-reviews",
    ),
    path("reviews/<int:review_id>/", OwnReviewDetailView.as_view(), name="review-detail"),
]
