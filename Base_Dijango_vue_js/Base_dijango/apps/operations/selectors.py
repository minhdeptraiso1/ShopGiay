from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.db.models import (
    Count,
    DurationField,
    ExpressionWrapper,
    F,
    Max,
    OuterRef,
    Q,
    Subquery,
    Sum,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.catalog.models import (
    InventoryBalance,
    Product,
    ProductEvent,
    ProductVariant,
    RecommendationItem,
    RecommendationRequest,
    StockMovement,
)
from apps.exchanges.models import ExchangeRequest
from apps.orders.models import Order, OrderItem, OrderStatusHistory


def _recognized_orders(*, start: datetime, end: datetime):
    completed_at = (
        OrderStatusHistory.objects.filter(order_id=OuterRef("pk"), to_status=Order.Status.COMPLETED)
        .order_by("-created_at")
        .values("created_at")[:1]
    )
    return (
        Order.objects.filter(payment_status=Order.PaymentStatus.PAID)
        .exclude(status=Order.Status.CANCELLED)
        .annotate(recognized_at=Coalesce("payment__paid_at", Subquery(completed_at), "updated_at"))
        .filter(recognized_at__gte=start, recognized_at__lt=end)
    )


def _percent_change(current: Decimal, previous: Decimal) -> Decimal | None:
    if previous == 0:
        return None if current else Decimal("0")
    return ((current - previous) * Decimal("100") / previous).quantize(Decimal("0.01"))


def get_dashboard(
    *, start: datetime, end: datetime, timezone_name: str, include_finance: bool
) -> dict:
    zone = ZoneInfo(timezone_name)
    duration = end - start
    previous_start = start - duration
    current_orders = _recognized_orders(start=start, end=end)
    previous_orders = _recognized_orders(start=previous_start, end=start)
    revenue = current_orders.aggregate(value=Coalesce(Sum("total"), Decimal("0")))["value"]
    order_ids = list(current_orders.values_list("id", flat=True))
    net_revenue = current_orders.aggregate(
        value=Coalesce(Sum(F("subtotal") - F("discount_total")), Decimal("0"))
    )["value"]
    cogs = OrderItem.objects.filter(order_id__in=order_ids).aggregate(
        value=Coalesce(Sum("cost_total"), Decimal("0"))
    )["value"]
    previous_revenue = previous_orders.aggregate(value=Coalesce(Sum("total"), Decimal("0")))[
        "value"
    ]
    order_count = current_orders.count()
    average_order_value = revenue / order_count if order_count else Decimal("0")
    queue = {
        row["status"]: row["count"]
        for row in Order.objects.values("status").annotate(count=Count("id"))
    }
    low_stock_count = InventoryBalance.objects.filter(
        variant__is_active=True,
        quantity__lte=F("variant__low_stock_threshold"),
    ).count()
    daily = defaultdict(lambda: Decimal("0"))
    for recognized_at, total in current_orders.values_list("recognized_at", "total"):
        daily[timezone.localtime(recognized_at, zone).date().isoformat()] += total
    recent = list(
        OrderStatusHistory.objects.select_related("order", "actor")
        .order_by("-created_at")
        .values("order__number", "to_status", "actor__email", "created_at")[:8]
    )
    payload = {
        "range": {"start": start.isoformat(), "end": end.isoformat(), "timezone": timezone_name},
        "queue": queue,
        "low_stock_count": low_stock_count,
        "recent_activity": recent,
        "revenue_series": [
            {"date": key, "revenue": str(value)} for key, value in sorted(daily.items())
        ],
        "finance": None,
    }
    if include_finance:
        payload["finance"] = {
            "revenue": str(revenue),
            "revenue_change_percent": (
                str(change)
                if (change := _percent_change(revenue, previous_revenue)) is not None
                else None
            ),
            "paid_order_count": order_count,
            "average_order_value": str(average_order_value.quantize(Decimal("1"))),
            "net_revenue": str(net_revenue),
            "cost_of_goods_sold": str(cogs),
            "profit": str(net_revenue - cogs),
        }
    return payload


def get_sales_report(*, start: datetime, end: datetime, timezone_name: str) -> dict:
    zone = ZoneInfo(timezone_name)
    recognized = _recognized_orders(start=start, end=end)
    order_ids = list(recognized.values_list("id", flat=True))
    revenue = recognized.aggregate(value=Coalesce(Sum("total"), Decimal("0")))["value"]
    net_revenue = recognized.aggregate(
        value=Coalesce(Sum(F("subtotal") - F("discount_total")), Decimal("0"))
    )["value"]
    cogs = OrderItem.objects.filter(order_id__in=order_ids).aggregate(
        value=Coalesce(Sum("cost_total"), Decimal("0"))
    )["value"]
    created = Order.objects.filter(created_at__gte=start, created_at__lt=end)
    cancelled = created.filter(status=Order.Status.CANCELLED).count()
    daily = defaultdict(lambda: {"revenue": Decimal("0"), "orders": 0})
    for recognized_at, total in recognized.values_list("recognized_at", "total"):
        key = timezone.localtime(recognized_at, zone).date().isoformat()
        daily[key]["revenue"] += total
        daily[key]["orders"] += 1
    best_sellers = list(
        OrderItem.objects.filter(order_id__in=order_ids)
        .values("variant__product_id", "product_name")
        .annotate(quantity=Sum("quantity"), net_revenue=Sum("line_total"))
        .order_by("-quantity", "-net_revenue")[:20]
    )
    cancellation_reasons = list(
        OrderStatusHistory.objects.filter(
            to_status=Order.Status.CANCELLED,
            created_at__gte=start,
            created_at__lt=end,
        )
        .values("note")
        .annotate(count=Count("id"))
        .order_by("-count", "note")
    )
    count = len(order_ids)
    return {
        "summary": {
            "revenue": str(revenue),
            "net_revenue": str(net_revenue),
            "cost_of_goods_sold": str(cogs),
            "profit": str(net_revenue - cogs),
            "paid_orders": count,
            "average_order_value": str((revenue / count).quantize(Decimal("1")) if count else 0),
            "cancelled_orders": cancelled,
            "cancellation_rate_percent": str(
                (Decimal(cancelled * 100) / created.count()).quantize(Decimal("0.01"))
                if created.exists()
                else 0
            ),
        },
        "daily": [
            {"date": key, "revenue": str(value["revenue"]), "orders": value["orders"]}
            for key, value in sorted(daily.items())
        ],
        "best_sellers": [
            {
                "product_id": row["variant__product_id"],
                "product_name": row["product_name"],
                "quantity": row["quantity"],
                "net_revenue": str(row["net_revenue"]),
            }
            for row in best_sellers
        ],
        "cancellation_reasons": [
            {"reason": row["note"] or "Không ghi chú", "count": row["count"]}
            for row in cancellation_reasons
        ],
    }


def get_inventory_report(*, start: datetime, end: datetime) -> dict:
    variants = ProductVariant.objects.select_related("product", "inventory").annotate(
        last_receipt_at=Max(
            "stock_movements__created_at",
            filter=Q(stock_movements__delta__gt=0),
        )
    )
    now = timezone.now()
    low_stock = []
    ageing = []
    for variant in variants:
        balance = getattr(variant, "inventory", None)
        quantity = balance.quantity if balance else 0
        item = {
            "variant_id": variant.id,
            "sku": variant.sku,
            "product_name": variant.product.name,
            "quantity": quantity,
            "threshold": variant.low_stock_threshold,
        }
        if variant.is_active and quantity <= variant.low_stock_threshold:
            low_stock.append(item)
        age_days = (now - (variant.last_receipt_at or variant.created_at)).days
        ageing.append({**item, "age_days": age_days, "last_receipt_at": variant.last_receipt_at})
    movements = StockMovement.objects.filter(created_at__gte=start, created_at__lt=end)
    movement_summary = list(
        movements.values("kind")
        .annotate(movements=Count("id"), net_quantity=Sum("delta"))
        .order_by("kind")
    )
    return {
        "summary": {
            "active_skus": variants.filter(is_active=True).count(),
            "low_stock_skus": len(low_stock),
            "units_on_hand": InventoryBalance.objects.aggregate(value=Coalesce(Sum("quantity"), 0))[
                "value"
            ],
        },
        "low_stock": sorted(low_stock, key=lambda row: (row["quantity"], row["sku"])),
        "ageing": sorted(ageing, key=lambda row: (-row["age_days"], row["sku"]))[:50],
        "movement_summary": movement_summary,
    }


def get_returns_report(*, start: datetime, end: datetime) -> dict:
    exchanges = ExchangeRequest.objects.filter(created_at__gte=start, created_at__lt=end)
    completed = exchanges.filter(status=ExchangeRequest.Status.COMPLETED).annotate(
        processing_time=ExpressionWrapper(
            F("updated_at") - F("created_at"), output_field=DurationField()
        )
    )
    durations = [row.processing_time.total_seconds() / 3600 for row in completed]
    eligible_orders = Order.objects.filter(
        status=Order.Status.COMPLETED, updated_at__gte=start, updated_at__lt=end
    ).count()
    count = exchanges.count()
    return {
        "summary": {
            "requests": count,
            "completed": completed.count(),
            "exchange_rate_percent": str(
                (Decimal(count * 100) / eligible_orders).quantize(Decimal("0.01"))
                if eligible_orders
                else 0
            ),
            "average_processing_hours": str(
                Decimal(sum(durations) / len(durations)).quantize(Decimal("0.1"))
                if durations
                else 0
            ),
        },
        "by_status": list(
            exchanges.values("status").annotate(count=Count("id")).order_by("status")
        ),
    }


def get_recommendation_report(*, start: datetime, end: datetime) -> dict:
    requests = RecommendationRequest.objects.filter(created_at__gte=start, created_at__lt=end)
    active_products = Product.objects.filter(status=Product.Status.PUBLISHED).count()
    rows = []
    for strategy in RecommendationRequest.Strategy.values:
        strategy_requests = requests.filter(strategy=strategy)
        request_ids = list(strategy_requests.values_list("id", flat=True))
        events = ProductEvent.objects.filter(
            created_at__gte=start,
            created_at__lt=end,
            recommendation_context_id__in=request_ids,
        )
        impressions = events.filter(
            event_type=ProductEvent.EventType.RECOMMENDATION_IMPRESSION
        ).count()
        clicks = events.filter(event_type=ProductEvent.EventType.RECOMMENDATION_CLICK).count()
        recommended = (
            RecommendationItem.objects.filter(request_id__in=request_ids)
            .values("product_id")
            .distinct()
            .count()
        )
        rows.append(
            {
                "strategy": strategy,
                "requests": len(request_ids),
                "impressions": impressions,
                "clicks": clicks,
                "ctr_percent": str(
                    (Decimal(clicks * 100) / impressions).quantize(Decimal("0.01"))
                    if impressions
                    else 0
                ),
                "add_to_carts": events.filter(event_type=ProductEvent.EventType.ADD_CART).count(),
                "purchases": events.filter(event_type=ProductEvent.EventType.PURCHASE).count(),
                "coverage_percent": str(
                    (Decimal(recommended * 100) / active_products).quantize(Decimal("0.01"))
                    if active_products
                    else 0
                ),
            }
        )
    return {"strategies": rows}
