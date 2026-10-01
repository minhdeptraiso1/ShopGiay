from collections import defaultdict
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db.models import Min, Sum
from django.utils import timezone

from apps.orders.models import OrderItem

from .models import Product, ProductEvent, RecommendationItem, RecommendationRequest
from .selectors import list_public_products

User = get_user_model()


@dataclass(frozen=True)
class RecommendationResult:
    request: RecommendationRequest
    products: list[Product]
    fallback_used: bool = False


EVENT_WEIGHTS = {
    ProductEvent.EventType.VIEW: Decimal("1"),
    ProductEvent.EventType.RECOMMENDATION_CLICK: Decimal("2"),
    ProductEvent.EventType.WISHLIST_ADD: Decimal("4"),
    ProductEvent.EventType.ADD_CART: Decimal("6"),
    ProductEvent.EventType.PURCHASE: Decimal("12"),
}


def _available_products() -> list[Product]:
    return list(list_public_products(in_stock=True))


def _store_result(
    *,
    strategy: str,
    products: list[Product],
    scores: dict[int, Decimal],
    user: User | None,
    anonymous_id: UUID | None,
    source_product: Product | None = None,
    fallback_used: bool = False,
) -> RecommendationResult:
    request = RecommendationRequest.objects.create(
        strategy=strategy,
        user=user,
        anonymous_id=anonymous_id,
        source_product=source_product,
    )
    RecommendationItem.objects.bulk_create(
        [
            RecommendationItem(
                request=request,
                product=product,
                rank=rank,
                score=scores.get(product.id, Decimal("0")),
            )
            for rank, product in enumerate(products, start=1)
        ]
    )
    return RecommendationResult(request=request, products=products, fallback_used=fallback_used)


def _popular_scores(*, candidates: list[Product]) -> dict[int, Decimal]:
    candidate_ids = {product.id for product in candidates}
    scores: dict[int, Decimal] = defaultdict(Decimal)
    now = timezone.now()
    events = ProductEvent.objects.filter(
        product_id__in=candidate_ids,
        event_type__in=EVENT_WEIGHTS,
        created_at__gte=now - timedelta(days=30),
    ).values("product_id", "event_type", "created_at")
    for event in events:
        recency = Decimal("2") if event["created_at"] >= now - timedelta(days=7) else Decimal("1")
        scores[event["product_id"]] += EVENT_WEIGHTS[event["event_type"]] * recency

    purchases = (
        OrderItem.objects.filter(
            product_slug__in=[product.slug for product in candidates],
            order__status="completed",
            order__updated_at__gte=now - timedelta(days=90),
        )
        .values("product_slug")
        .annotate(quantity=Sum("quantity"))
    )
    ids_by_slug = {product.slug: product.id for product in candidates}
    for row in purchases:
        product_id = ids_by_slug.get(row["product_slug"])
        if product_id:
            scores[product_id] += Decimal(row["quantity"] or 0) * Decimal("20")
    return scores


def popular_recommendations(
    *, user: User | None, anonymous_id: UUID | None, limit: int = 8
) -> RecommendationResult:
    candidates = _available_products()
    scores = _popular_scores(candidates=candidates)
    ranked = sorted(
        candidates,
        key=lambda product: (
            scores.get(product.id, Decimal("0")),
            product.published_at or product.created_at,
        ),
        reverse=True,
    )[:limit]
    return _store_result(
        strategy=RecommendationRequest.Strategy.POPULAR,
        products=ranked,
        scores=scores,
        user=user,
        anonymous_id=anonymous_id,
    )


def similar_recommendations(
    *, source: Product, user: User | None, anonymous_id: UUID | None, limit: int = 6
) -> RecommendationResult:
    candidates = [product for product in _available_products() if product.id != source.id]
    source_price = source.variants.filter(is_active=True).aggregate(value=Min("price"))[
        "value"
    ] or Decimal("0")
    scores: dict[int, Decimal] = {}
    for product in candidates:
        score = Decimal("0")
        if product.category_id == source.category_id:
            score += Decimal("7")
        if product.brand_id == source.brand_id:
            score += Decimal("3")
        if product.product_type == source.product_type:
            score += Decimal("3")
        price = min((variant.price for variant in product.public_variants), default=Decimal("0"))
        if source_price and price:
            difference = abs(price - source_price) / source_price
            score += max(Decimal("0"), Decimal("3") - difference * Decimal("3"))
        scores[product.id] = score
    ranked = sorted(candidates, key=lambda product: scores[product.id], reverse=True)
    if source.product_type == Product.ProductType.FOOTWEAR and limit >= 3:
        companions = [
            product
            for product in ranked
            if product.product_type in {Product.ProductType.ACCESSORY, Product.ProductType.CARE}
        ][:2]
        primary = [product for product in ranked if product not in companions][
            : limit - len(companions)
        ]
        ranked = primary + companions
    else:
        ranked = ranked[:limit]
    return _store_result(
        strategy=RecommendationRequest.Strategy.SIMILAR,
        products=ranked,
        scores=scores,
        user=user,
        anonymous_id=anonymous_id,
        source_product=source,
    )


def personalized_recommendations(
    *, user: User | None, anonymous_id: UUID | None, limit: int = 8
) -> RecommendationResult:
    interactions = ProductEvent.objects.filter(created_at__gte=timezone.now() - timedelta(days=90))
    if user:
        interactions = interactions.filter(user=user)
    elif anonymous_id:
        interactions = interactions.filter(anonymous_id=anonymous_id)
    else:
        interactions = interactions.none()
    interactions = list(interactions.select_related("product__category", "product__brand"))
    if not interactions:
        popular = popular_recommendations(user=user, anonymous_id=anonymous_id, limit=limit)
        return RecommendationResult(popular.request, popular.products, fallback_used=True)

    category_scores: dict[int, Decimal] = defaultdict(Decimal)
    brand_scores: dict[int, Decimal] = defaultdict(Decimal)
    type_scores: dict[str, Decimal] = defaultdict(Decimal)
    seen_ids: set[int] = set()
    for event in interactions:
        weight = EVENT_WEIGHTS.get(event.event_type, Decimal("0"))
        category_scores[event.product.category_id] += weight
        brand_scores[event.product.brand_id] += weight
        type_scores[event.product.product_type] += weight
        seen_ids.add(event.product_id)

    candidates = _available_products()
    popularity = _popular_scores(candidates=candidates)
    scores: dict[int, Decimal] = {}
    for product in candidates:
        score = (
            category_scores[product.category_id] * Decimal("1.5")
            + brand_scores[product.brand_id]
            + type_scores[product.product_type]
            + popularity.get(product.id, Decimal("0")) * Decimal("0.15")
        )
        if product.id in seen_ids:
            score *= Decimal("0.35")
        scores[product.id] = score
    ranked = sorted(candidates, key=lambda product: scores[product.id], reverse=True)[:limit]
    return _store_result(
        strategy=RecommendationRequest.Strategy.PERSONALIZED,
        products=ranked,
        scores=scores,
        user=user,
        anonymous_id=anonymous_id,
    )
