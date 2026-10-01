import uuid
from dataclasses import dataclass
from decimal import ROUND_DOWN, Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.catalog.models import Product, ProductEvent
from apps.orders.models import CartItem, Order, OrderItem

from .models import Banner, Review, Voucher, VoucherAllocation, VoucherUsage, WishlistItem

User = get_user_model()
ACTIVE_USAGE_STATUSES = (VoucherUsage.Status.RESERVED, VoucherUsage.Status.REDEEMED)


class VoucherValidationError(Exception):
    pass


class ReviewEligibilityError(Exception):
    pass


@dataclass(frozen=True)
class VoucherQuote:
    voucher: Voucher | None
    code: str
    discount_total: Decimal
    allocations: dict[int, Decimal]


def _allocate_discount(
    *, discount: Decimal, eligible_lines: list[tuple[int, Decimal]]
) -> dict[int, Decimal]:
    if discount <= 0 or not eligible_lines:
        return {}
    eligible_total = sum((amount for _, amount in eligible_lines), Decimal("0"))
    allocations: dict[int, Decimal] = {}
    fractions: list[tuple[Decimal, int]] = []
    allocated = Decimal("0")
    for variant_id, amount in eligible_lines:
        raw = discount * amount / eligible_total
        floor = raw.quantize(Decimal("1"), rounding=ROUND_DOWN)
        allocations[variant_id] = floor
        allocated += floor
        fractions.append((raw - floor, variant_id))
    remainder = int(discount - allocated)
    for _, variant_id in sorted(fractions, key=lambda item: (-item[0], item[1]))[:remainder]:
        allocations[variant_id] += Decimal("1")
    return allocations


def calculate_voucher_quote(
    *, user: User, code: str, items: list[CartItem], subtotal: Decimal, lock: bool = False
) -> VoucherQuote:
    normalized = code.strip().upper()
    if not normalized:
        return VoucherQuote(None, "", Decimal("0"), {})
    queryset = Voucher.objects.select_for_update() if lock else Voucher.objects.all()
    try:
        voucher = queryset.prefetch_related("products", "categories").get(code=normalized)
    except Voucher.DoesNotExist as exc:
        raise VoucherValidationError("Mã giảm giá không tồn tại.") from exc
    now = timezone.now()
    if not voucher.is_active or not (voucher.starts_at <= now < voucher.ends_at):
        raise VoucherValidationError("Mã giảm giá chưa có hiệu lực hoặc đã hết hạn.")
    points_balance = getattr(getattr(user, "loyalty_account", None), "balance", 0)
    if points_balance < voucher.required_points:
        raise VoucherValidationError(
            f"Bạn cần tối thiểu {voucher.required_points} điểm để dùng voucher này."
        )
    if subtotal < voucher.min_order_value:
        raise VoucherValidationError(
            f"Đơn hàng phải đạt tối thiểu {voucher.min_order_value:.0f} VND."
        )
    active_usages = voucher.usages.filter(status__in=ACTIVE_USAGE_STATUSES)
    if voucher.usage_limit is not None and active_usages.count() >= voucher.usage_limit:
        raise VoucherValidationError("Mã giảm giá đã hết lượt sử dụng.")
    if active_usages.filter(user=user).count() >= voucher.per_user_limit:
        raise VoucherValidationError("Bạn đã sử dụng hết lượt của mã giảm giá này.")

    product_ids = set(voucher.products.values_list("id", flat=True))
    category_ids = set(voucher.categories.values_list("id", flat=True))
    eligible_lines: list[tuple[int, Decimal]] = []
    for item in items:
        product = item.variant.product
        if not product_ids and not category_ids:
            eligible = True
        else:
            eligible = product.id in product_ids or product.category_id in category_ids
        if eligible:
            eligible_lines.append((item.variant_id, item.variant.price * item.quantity))
    eligible_total = sum((amount for _, amount in eligible_lines), Decimal("0"))
    if eligible_total <= 0:
        raise VoucherValidationError("Mã giảm giá không áp dụng cho sản phẩm trong giỏ hàng.")
    if voucher.discount_type == Voucher.DiscountType.PERCENT:
        discount = (eligible_total * voucher.value / Decimal("100")).quantize(Decimal("1"))
        if voucher.max_discount is not None:
            discount = min(discount, voucher.max_discount)
    else:
        discount = voucher.value
    discount = min(discount, eligible_total)
    return VoucherQuote(
        voucher=voucher,
        code=voucher.code,
        discount_total=discount,
        allocations=_allocate_discount(discount=discount, eligible_lines=eligible_lines),
    )


def create_voucher_usage(
    *,
    quote: VoucherQuote,
    user: User,
    order: Order,
    order_items: list[OrderItem],
    reserved: bool,
) -> VoucherUsage | None:
    if quote.voucher is None:
        return None
    usage = VoucherUsage.objects.create(
        voucher=quote.voucher,
        user=user,
        order=order,
        status=VoucherUsage.Status.RESERVED if reserved else VoucherUsage.Status.REDEEMED,
        discount_amount=quote.discount_total,
    )
    VoucherAllocation.objects.bulk_create(
        [
            VoucherAllocation(
                usage=usage,
                order_item=item,
                amount=quote.allocations.get(item.variant_id, Decimal("0")),
            )
            for item in order_items
            if quote.allocations.get(item.variant_id, Decimal("0")) > 0
        ]
    )
    return usage


def redeem_order_voucher(*, order: Order) -> None:
    VoucherUsage.objects.filter(order=order, status=VoucherUsage.Status.RESERVED).update(
        status=VoucherUsage.Status.REDEEMED, updated_at=timezone.now()
    )


def release_order_voucher(*, order: Order) -> None:
    VoucherUsage.objects.filter(order=order, status__in=ACTIVE_USAGE_STATUSES).update(
        status=VoucherUsage.Status.RELEASED, updated_at=timezone.now()
    )


@transaction.atomic
def toggle_wishlist(*, user: User, product: Product) -> tuple[WishlistItem | None, bool]:
    item = WishlistItem.objects.select_for_update().filter(user=user, product=product).first()
    if item:
        item.delete()
        event_type = ProductEvent.EventType.WISHLIST_REMOVE
        active = False
        result = None
    else:
        result = WishlistItem.objects.create(user=user, product=product)
        event_type = ProductEvent.EventType.WISHLIST_ADD
        active = True
    ProductEvent.objects.create(
        client_event_id=uuid.uuid4(),
        schema_version=1,
        event_type=event_type,
        source=ProductEvent.Source.STOREFRONT,
        product=product,
        user=user,
    )
    return result, active


def remove_wishlist_item(*, user: User, product_id: int) -> None:
    item = WishlistItem.objects.filter(user=user, product_id=product_id).first()
    if item:
        item.delete()
        ProductEvent.objects.create(
            client_event_id=uuid.uuid4(),
            schema_version=1,
            event_type=ProductEvent.EventType.WISHLIST_REMOVE,
            source=ProductEvent.Source.STOREFRONT,
            product_id=product_id,
            user=user,
        )


@transaction.atomic
def create_review(
    *, user: User, product: Product, order_item_id: int, rating: int, content: str
) -> Review:
    try:
        order_item = OrderItem.objects.select_related("order", "variant__product").get(
            pk=order_item_id, order__user=user
        )
    except OrderItem.DoesNotExist as exc:
        raise ReviewEligibilityError("Sản phẩm trong đơn hàng không tồn tại.") from exc
    if order_item.variant.product_id != product.id:
        raise ReviewEligibilityError("Sản phẩm đánh giá không khớp với đơn hàng.")
    if order_item.order.status != Order.Status.COMPLETED:
        raise ReviewEligibilityError("Chỉ có thể đánh giá sản phẩm từ đơn đã hoàn tất.")
    if Review.objects.filter(order_item=order_item).exists():
        raise ReviewEligibilityError("Sản phẩm trong đơn hàng này đã được đánh giá.")
    return Review.objects.create(
        user=user,
        product=product,
        order_item=order_item,
        rating=rating,
        content=content.strip(),
    )


def update_own_review(*, review: Review, rating: int, content: str) -> Review:
    review.rating = rating
    review.content = content.strip()
    review.status = Review.Status.PENDING
    review.moderation_note = ""
    review.moderated_by = None
    review.moderated_at = None
    review.save()
    return review


def moderate_review(*, review: Review, moderator: User, status: str, note: str) -> Review:
    review.status = status
    review.moderation_note = note.strip()
    review.moderated_by = moderator
    review.moderated_at = timezone.now()
    review.save(
        update_fields=[
            "status",
            "moderation_note",
            "moderated_by",
            "moderated_at",
            "updated_at",
        ]
    )
    return review


def save_voucher(*, instance: Voucher | None, data: dict) -> Voucher:
    products = data.pop("products", None)
    categories = data.pop("categories", None)
    voucher = instance or Voucher()
    for field, value in data.items():
        setattr(voucher, field, value)
    voucher.save()
    if products is not None:
        voucher.products.set(products)
    if categories is not None:
        voucher.categories.set(categories)
    return voucher


def save_banner(*, instance: Banner | None, data: dict) -> Banner:
    banner = instance or Banner()
    for field, value in data.items():
        setattr(banner, field, value)
    banner.save()
    return banner
