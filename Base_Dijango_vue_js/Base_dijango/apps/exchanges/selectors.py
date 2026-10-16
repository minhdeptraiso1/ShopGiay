from django.db.models import Prefetch, Q, QuerySet

from .models import ExchangeItem, ExchangeRequest


def _exchange_queryset() -> QuerySet[ExchangeRequest]:
    items = ExchangeItem.objects.select_related(
        "order_item__variant__product",
        "target_variant__product",
        "target_variant__size",
        "target_variant__color",
    )
    return ExchangeRequest.objects.select_related("order", "user", "approved_by").prefetch_related(
        Prefetch("items", queryset=items), "status_history__actor"
    )


def list_customer_exchanges(*, user_id: int) -> QuerySet[ExchangeRequest]:
    return _exchange_queryset().filter(user_id=user_id)


def get_customer_exchange(*, user_id: int, exchange_id: int) -> ExchangeRequest:
    return _exchange_queryset().get(user_id=user_id, pk=exchange_id)


def list_admin_exchanges(
    *, status: str = "", search: str = "", start_date: str = "", end_date: str = ""
) -> QuerySet[ExchangeRequest]:
    queryset = _exchange_queryset()
    if status in ExchangeRequest.Status.values:
        queryset = queryset.filter(status=status)
    if search := search.strip():
        queryset = queryset.filter(
            Q(order__number__icontains=search)
            | Q(user__email__icontains=search)
            | Q(tracking_number__icontains=search)
        )
    if start_date:
        queryset = queryset.filter(created_at__date__gte=start_date)
    if end_date:
        queryset = queryset.filter(created_at__date__lte=end_date)
    return queryset


def get_admin_exchange(*, exchange_id: int) -> ExchangeRequest:
    return _exchange_queryset().get(pk=exchange_id)
