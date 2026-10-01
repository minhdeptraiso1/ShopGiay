from django.db.models import Prefetch, QuerySet

from apps.catalog.models import ProductImage

from .models import Cart, CartItem, Order


def get_user_cart(*, user_id: int) -> Cart:
    return Cart.objects.prefetch_related(
        Prefetch(
            "items",
            queryset=CartItem.objects.select_related(
                "variant__product__brand",
                "variant__product__category",
                "variant__size",
                "variant__color",
                "variant__inventory",
            ).prefetch_related(
                Prefetch(
                    "variant__product__images",
                    queryset=ProductImage.objects.order_by("sort_order", "id"),
                )
            ),
        )
    ).get(user_id=user_id)


def list_user_orders(*, user_id: int) -> QuerySet[Order]:
    return Order.objects.filter(user_id=user_id).prefetch_related("items", "status_history__actor")


def get_user_order(*, user_id: int, order_id: int) -> Order:
    return (
        Order.objects.filter(user_id=user_id)
        .select_related("address")
        .prefetch_related("items", "status_history__actor")
        .get(pk=order_id)
    )


def list_admin_orders(*, status: str | None = None) -> QuerySet[Order]:
    queryset = get_admin_order()
    if status in Order.Status.values:
        queryset = queryset.filter(status=status)
    return queryset


def get_admin_order() -> QuerySet[Order]:
    return Order.objects.select_related("user", "address").prefetch_related(
        "items", "status_history__actor"
    )
