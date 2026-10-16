from django.db.models import Prefetch, Q, QuerySet
from django.utils import timezone

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


def list_admin_orders(
    *,
    status: str | None = None,
    search: str = "",
    start_date: str = "",
    end_date: str = "",
    today: bool = False,
) -> QuerySet[Order]:
    queryset = get_admin_order()
    if status in Order.Status.values:
        queryset = queryset.filter(status=status)
    if search := search.strip():
        queryset = queryset.filter(
            Q(number__icontains=search)
            | Q(user__email__icontains=search)
            | Q(recipient_name__icontains=search)
            | Q(phone_number__icontains=search)
        )
    if today:
        queryset = queryset.filter(created_at__date=timezone.localdate())
    else:
        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)
    return queryset


def get_admin_order() -> QuerySet[Order]:
    return Order.objects.select_related("user", "address").prefetch_related(
        "items", "status_history__actor"
    )
