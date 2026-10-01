from decimal import Decimal

from django.db.models import Min, Prefetch, Q, QuerySet
from django.shortcuts import get_object_or_404

from .models import Brand, Category, Color, Product, ProductImage, ProductVariant, Size


def list_public_categories() -> QuerySet[Category]:
    return Category.objects.filter(is_active=True).select_related("parent")


def list_public_brands() -> QuerySet[Brand]:
    return Brand.objects.filter(is_active=True)


def list_public_sizes(*, brand: str = "") -> QuerySet[Size]:
    queryset = Size.objects.filter(is_active=True, brand__is_active=True).select_related("brand")
    return queryset.filter(brand__slug=brand) if brand else queryset


def list_public_colors() -> QuerySet[Color]:
    return Color.objects.filter(is_active=True)


def list_public_products(
    *,
    search: str = "",
    category: str = "",
    brand: str = "",
    size: str = "",
    color: str = "",
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    in_stock: bool | None = None,
    ordering: str = "newest",
) -> QuerySet[Product]:
    active_variants = (
        ProductVariant.objects.filter(is_active=True)
        .filter(
            Q(size__isnull=True) | Q(size__is_active=True),
            Q(color__isnull=True) | Q(color__is_active=True),
        )
        .select_related("size", "color", "inventory")
    )
    queryset = (
        Product.objects.filter(
            status=Product.Status.PUBLISHED,
            category__is_active=True,
            brand__is_active=True,
        )
        .select_related("category", "brand")
        .prefetch_related(
            Prefetch("variants", queryset=active_variants, to_attr="public_variants"),
            Prefetch("images", queryset=ProductImage.objects.order_by("sort_order", "id")),
        )
        .annotate(min_variant_price=Min("variants__price", filter=Q(variants__is_active=True)))
    )
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
            | Q(variants__sku__icontains=search)
            | Q(brand__name__icontains=search)
            | Q(category__name__icontains=search)
        )
    if category:
        queryset = queryset.filter(category__slug=category)
    if brand:
        queryset = queryset.filter(brand__slug=brand)
    if size:
        queryset = queryset.filter(variants__size__label=size, variants__is_active=True)
    if color:
        queryset = queryset.filter(variants__color__slug=color, variants__is_active=True)
    if min_price is not None:
        queryset = queryset.filter(variants__price__gte=min_price, variants__is_active=True)
    if max_price is not None:
        queryset = queryset.filter(variants__price__lte=max_price, variants__is_active=True)
    if in_stock is True:
        queryset = queryset.filter(variants__is_active=True, variants__inventory__quantity__gt=0)
    if in_stock is False:
        queryset = queryset.exclude(variants__is_active=True, variants__inventory__quantity__gt=0)
    order_map = {
        "newest": "-created_at",
        "name": "name",
        "-name": "-name",
        "price": "min_variant_price",
        "-price": "-min_variant_price",
    }
    return queryset.distinct().order_by(order_map.get(ordering, "-created_at"))


def get_public_product(*, slug: str) -> Product:
    return get_object_or_404(list_public_products(), slug=slug)


def list_brand_sizes(*, brand_id: int) -> QuerySet[Size]:
    return Size.objects.filter(brand_id=brand_id, is_active=True).select_related("brand")
