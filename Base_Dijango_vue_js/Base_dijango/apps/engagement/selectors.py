from django.db.models import Prefetch, QuerySet
from django.utils import timezone

from apps.catalog.models import ProductImage, ProductVariant

from .models import Banner, Review, WishlistItem


def list_active_banners(*, position: str = "") -> QuerySet[Banner]:
    now = timezone.now()
    queryset = Banner.objects.filter(is_active=True, starts_at__lte=now, ends_at__gt=now)
    return queryset.filter(position=position) if position else queryset


def list_wishlist(*, user_id: int) -> QuerySet[WishlistItem]:
    variants = ProductVariant.objects.filter(is_active=True).select_related(
        "size", "color", "inventory"
    )
    return (
        WishlistItem.objects.filter(user_id=user_id, product__status="published")
        .select_related("product__category", "product__brand")
        .prefetch_related(
            Prefetch("product__variants", queryset=variants, to_attr="public_variants"),
            Prefetch("product__images", queryset=ProductImage.objects.order_by("sort_order", "id")),
        )
    )


def list_public_reviews(*, product_id: int) -> QuerySet[Review]:
    return Review.objects.filter(
        product_id=product_id, status=Review.Status.APPROVED
    ).select_related("user")


def list_admin_reviews() -> QuerySet[Review]:
    return Review.objects.select_related("user", "product", "order_item", "moderated_by")
