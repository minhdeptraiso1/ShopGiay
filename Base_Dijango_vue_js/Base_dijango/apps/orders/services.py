import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import Address
from apps.catalog.models import (
    InventoryBalance,
    Product,
    ProductEvent,
    ProductVariant,
    StockMovement,
)

from .models import (
    Cart,
    CartItem,
    InventoryReservation,
    Order,
    OrderItem,
    OrderStatusHistory,
    Payment,
    PaymentAttempt,
)

User = get_user_model()


class CartItemUnavailableError(Exception):
    pass


class CartOwnershipError(Exception):
    pass


class InsufficientStockError(Exception):
    pass


class IdempotencyConflictError(Exception):
    pass


class OrderCancellationError(Exception):
    pass


class OrderReceiptConfirmationError(Exception):
    pass


@dataclass(frozen=True)
class QuoteLine:
    cart_item_id: int
    variant_id: int
    sku: str
    product_name: str
    size_label: str
    color_name: str
    quantity: int
    unit_price: Decimal
    discount_total: Decimal
    line_total: Decimal
    currency: str


@dataclass(frozen=True)
class CheckoutQuote:
    address_id: int
    lines: tuple[QuoteLine, ...]
    subtotal: Decimal
    shipping_fee: Decimal
    discount_total: Decimal
    total: Decimal
    currency: str
    voucher_code: str
    voucher_id: int | None


def _is_variant_purchasable(variant: ProductVariant) -> bool:
    return bool(
        variant.is_active
        and variant.product.status == Product.Status.PUBLISHED
        and variant.product.category.is_active
        and variant.product.brand.is_active
        and variant.size.is_active
        and variant.color.is_active
    )


def _get_inventory_quantity(variant: ProductVariant) -> int:
    inventory = getattr(variant, "inventory", None)
    return inventory.quantity if inventory else 0


def ensure_user_cart(*, user: User) -> Cart:
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@transaction.atomic
def add_cart_item(
    *,
    user: User,
    variant: ProductVariant,
    quantity: int,
    recommendation_context_id=None,
) -> CartItem:
    User.objects.select_for_update().get(pk=user.pk)
    variant = ProductVariant.objects.select_related(
        "product__category", "product__brand", "size", "color", "inventory"
    ).get(pk=variant.pk)
    if not _is_variant_purchasable(variant):
        raise CartItemUnavailableError("Variant hiện không khả dụng.")
    cart, _ = Cart.objects.get_or_create(user=user)
    item = CartItem.objects.select_for_update().filter(cart=cart, variant=variant).first()
    new_quantity = quantity + (item.quantity if item else 0)
    if new_quantity > _get_inventory_quantity(variant):
        raise InsufficientStockError("Số lượng yêu cầu vượt quá tồn kho hiện tại.")
    if item:
        item.quantity = new_quantity
        item.save(update_fields=["quantity", "updated_at"])
    else:
        item = CartItem.objects.create(cart=cart, variant=variant, quantity=new_quantity)
    valid_context_id = None
    if recommendation_context_id:
        has_eligible_click = ProductEvent.objects.filter(
            user=user,
            product=variant.product,
            event_type=ProductEvent.EventType.RECOMMENDATION_CLICK,
            recommendation_context_id=recommendation_context_id,
            created_at__gte=timezone.now() - timedelta(days=7),
        ).exists()
        if has_eligible_click:
            valid_context_id = recommendation_context_id
    ProductEvent.objects.create(
        client_event_id=uuid.uuid4(),
        schema_version=1,
        event_type=ProductEvent.EventType.ADD_CART,
        source=ProductEvent.Source.STOREFRONT,
        product=variant.product,
        user=user,
        recommendation_context_id=valid_context_id,
    )
    return item


@transaction.atomic
def update_cart_item(*, user: User, item: CartItem, quantity: int) -> CartItem:
    User.objects.select_for_update().get(pk=user.pk)
    locked_item = CartItem.objects.select_for_update().get(pk=item.pk, cart__user=user)
    item = CartItem.objects.select_related(
        "variant__product__category",
        "variant__product__brand",
        "variant__size",
        "variant__color",
        "variant__inventory",
    ).get(pk=locked_item.pk)
    if not _is_variant_purchasable(item.variant):
        raise CartItemUnavailableError("Variant hiện không khả dụng.")
    if quantity > _get_inventory_quantity(item.variant):
        raise InsufficientStockError("Số lượng yêu cầu vượt quá tồn kho hiện tại.")
    item.quantity = quantity
    item.save(update_fields=["quantity", "updated_at"])
    return item


def delete_cart_item(*, user: User, item: CartItem) -> None:
    deleted, _ = CartItem.objects.filter(pk=item.pk, cart__user=user).delete()
    if not deleted:
        raise CartOwnershipError("Sản phẩm không tồn tại trong giỏ hàng của bạn.")


def _load_cart_items(*, user: User, item_ids: list[int]) -> list[CartItem]:
    items = list(
        CartItem.objects.filter(cart__user=user, id__in=item_ids)
        .select_related(
            "variant__product__category",
            "variant__product__brand",
            "variant__size",
            "variant__color",
            "variant__inventory",
        )
        .order_by("id")
    )
    if len(items) != len(item_ids):
        raise CartOwnershipError("Một hoặc nhiều cart item không thuộc tài khoản của bạn.")
    return items


def _quote_from_items(
    *,
    user: User,
    address_id: int,
    items: list[CartItem],
    voucher_code: str = "",
    lock_voucher: bool = False,
) -> CheckoutQuote:
    gross_lines: list[tuple[CartItem, Decimal]] = []
    subtotal = Decimal("0")
    for item in items:
        variant = item.variant
        if not _is_variant_purchasable(variant):
            raise CartItemUnavailableError(f"SKU {variant.sku} hiện không khả dụng.")
        if item.quantity > _get_inventory_quantity(variant):
            raise InsufficientStockError(f"SKU {variant.sku} không đủ tồn kho.")
        line_total = variant.price * item.quantity
        subtotal += line_total
        gross_lines.append((item, line_total))
    from apps.engagement.services import calculate_voucher_quote

    voucher_quote = calculate_voucher_quote(
        user=user,
        code=voucher_code,
        items=items,
        subtotal=subtotal,
        lock=lock_voucher,
    )
    lines: list[QuoteLine] = []
    for item, gross_total in gross_lines:
        variant = item.variant
        line_discount = voucher_quote.allocations.get(variant.id, Decimal("0"))
        lines.append(
            QuoteLine(
                cart_item_id=item.id,
                variant_id=variant.id,
                sku=variant.sku,
                product_name=variant.product.name,
                size_label=variant.size.label if variant.size else variant.option_label,
                color_name=variant.color.name if variant.color else "",
                quantity=item.quantity,
                unit_price=variant.price,
                discount_total=line_discount,
                line_total=gross_total - line_discount,
                currency=variant.currency,
            )
        )
    shipping_fee = (
        Decimal("0") if subtotal >= settings.FREE_SHIPPING_THRESHOLD else settings.SHIPPING_FLAT_FEE
    )
    discount_total = voucher_quote.discount_total
    return CheckoutQuote(
        address_id=address_id,
        lines=tuple(lines),
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        discount_total=discount_total,
        total=subtotal + shipping_fee - discount_total,
        currency="VND",
        voucher_code=voucher_quote.code,
        voucher_id=voucher_quote.voucher.id if voucher_quote.voucher else None,
    )


def build_checkout_quote(
    *, user: User, address_id: int, cart_item_ids: list[int], voucher_code: str = ""
) -> CheckoutQuote:
    Address.objects.get(pk=address_id, user=user)
    return _quote_from_items(
        user=user,
        address_id=address_id,
        items=_load_cart_items(user=user, item_ids=cart_item_ids),
        voucher_code=voucher_code,
    )


def _request_fingerprint(
    *,
    address_id: int,
    item_ids: list[int],
    payment_method: str = Order.PaymentMethod.COD,
    voucher_code: str = "",
) -> str:
    data: dict[str, object] = {"address_id": address_id, "cart_item_ids": sorted(item_ids)}
    if payment_method != Order.PaymentMethod.COD:
        data["payment_method"] = payment_method
    if voucher_code.strip():
        data["voucher_code"] = voucher_code.strip().upper()
    payload = json.dumps(data, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def _new_order_number() -> str:
    return f"ORD-{timezone.now():%Y%m%d}-{uuid.uuid4().hex[:10].upper()}"


@transaction.atomic
def create_order(
    *,
    user: User,
    address_id: int,
    cart_item_ids: list[int],
    idempotency_key: uuid.UUID,
    payment_method: str = Order.PaymentMethod.COD,
    voucher_code: str = "",
) -> tuple[Order, bool]:
    User.objects.select_for_update().get(pk=user.pk)
    fingerprint = _request_fingerprint(
        address_id=address_id,
        item_ids=cart_item_ids,
        payment_method=payment_method,
        voucher_code=voucher_code,
    )
    existing = Order.objects.filter(user=user, idempotency_key=idempotency_key).first()
    if existing:
        if existing.request_fingerprint != fingerprint:
            raise IdempotencyConflictError("Idempotency key đã được dùng với request khác.")
        return existing, False

    address = Address.objects.get(pk=address_id, user=user)
    items = _load_cart_items(user=user, item_ids=cart_item_ids)
    variant_ids = sorted(item.variant_id for item in items)
    balances = {
        balance.variant_id: balance
        for balance in InventoryBalance.objects.select_for_update()
        .filter(variant_id__in=variant_ids)
        .order_by("variant_id")
    }
    for item in items:
        item.variant.inventory = balances.get(item.variant_id)
    quote = _quote_from_items(
        user=user,
        address_id=address.id,
        items=items,
        voucher_code=voucher_code,
        lock_voucher=True,
    )

    order = Order.objects.create(
        user=user,
        address=address,
        number=_new_order_number(),
        idempotency_key=idempotency_key,
        request_fingerprint=fingerprint,
        payment_method=payment_method,
        subtotal=quote.subtotal,
        shipping_fee=quote.shipping_fee,
        discount_total=quote.discount_total,
        total=quote.total,
        recipient_name=address.recipient_name,
        phone_number=address.phone_number,
        province=address.province,
        district=address.district,
        ward=address.ward,
        street_address=address.street_address,
    )
    reservation_expires_at = timezone.now() + timedelta(
        minutes=settings.PAYMENT_RESERVATION_MINUTES
    )
    created_order_items: list[OrderItem] = []
    for item, line in zip(items, quote.lines, strict=True):
        balance = balances[item.variant_id]
        before = balance.quantity
        balance.quantity -= item.quantity
        balance.save(update_fields=["quantity", "updated_at"])
        order_item = OrderItem.objects.create(
            order=order,
            variant=item.variant,
            quantity=line.quantity,
            product_name=line.product_name,
            product_slug=item.variant.product.slug,
            sku=line.sku,
            size_label=line.size_label,
            color_name=line.color_name,
            unit_price=line.unit_price,
            discount_total=line.discount_total,
            line_total=line.line_total,
            currency=line.currency,
        )
        created_order_items.append(order_item)
        StockMovement.objects.create(
            variant=item.variant,
            kind=(
                StockMovement.Kind.SALE
                if payment_method == Order.PaymentMethod.COD
                else StockMovement.Kind.RESERVATION
            ),
            delta=-item.quantity,
            quantity_before=before,
            quantity_after=balance.quantity,
            reason=(
                f"Tạo đơn COD {order.number}"
                if payment_method == Order.PaymentMethod.COD
                else f"Giữ hàng cho đơn VNPay {order.number}"
            ),
            actor=user,
        )
        if payment_method == Order.PaymentMethod.VNPAY:
            InventoryReservation.objects.create(
                order_item=order_item,
                variant=item.variant,
                quantity=item.quantity,
                expires_at=reservation_expires_at,
            )
    if payment_method == Order.PaymentMethod.VNPAY:
        Payment.objects.create(
            order=order,
            provider=Payment.Provider.VNPAY,
            amount=order.total,
            currency=order.currency,
        )
    from apps.engagement.models import Voucher
    from apps.engagement.services import VoucherQuote, create_voucher_usage

    create_voucher_usage(
        quote=VoucherQuote(
            voucher=(
                Voucher.objects.get(pk=quote.voucher_id) if quote.voucher_id is not None else None
            ),
            code=quote.voucher_code,
            discount_total=quote.discount_total,
            allocations={line.variant_id: line.discount_total for line in quote.lines},
        ),
        user=user,
        order=order,
        order_items=created_order_items,
        reserved=payment_method == Order.PaymentMethod.VNPAY,
    )
    OrderStatusHistory.objects.create(
        order=order,
        from_status="",
        to_status=Order.Status.PENDING_CONFIRMATION,
        actor=user,
        note=(
            "Khách hàng tạo đơn COD"
            if payment_method == Order.PaymentMethod.COD
            else "Khách hàng tạo đơn VNPay và giữ tồn kho"
        ),
    )
    CartItem.objects.filter(pk__in=cart_item_ids, cart__user=user).delete()
    return order, True


def create_cod_order(
    *,
    user: User,
    address_id: int,
    cart_item_ids: list[int],
    idempotency_key: uuid.UUID,
) -> tuple[Order, bool]:
    return create_order(
        user=user,
        address_id=address_id,
        cart_item_ids=cart_item_ids,
        idempotency_key=idempotency_key,
        payment_method=Order.PaymentMethod.COD,
    )


@transaction.atomic
def release_order_inventory(*, order: Order, actor: User | None, reason: str) -> None:
    items = list(order.items.select_related("variant", "reservation").order_by("variant_id"))
    balances = {
        balance.variant_id: balance
        for balance in InventoryBalance.objects.select_for_update()
        .filter(variant_id__in=[item.variant_id for item in items])
        .order_by("variant_id")
    }
    for item in items:
        reservation = getattr(item, "reservation", None)
        if reservation and reservation.status != InventoryReservation.Status.ACTIVE:
            continue
        balance = balances[item.variant_id]
        before = balance.quantity
        balance.quantity += item.quantity
        balance.save(update_fields=["quantity", "updated_at"])
        StockMovement.objects.create(
            variant=item.variant,
            kind=(
                StockMovement.Kind.RESERVATION_RELEASE
                if reservation
                else StockMovement.Kind.CANCELLATION
            ),
            delta=item.quantity,
            quantity_before=before,
            quantity_after=balance.quantity,
            reason=reason,
            actor=actor,
        )
        if reservation:
            reservation.status = InventoryReservation.Status.RELEASED
            reservation.released_at = timezone.now()
            reservation.save(update_fields=["status", "released_at", "updated_at"])
    from apps.engagement.services import release_order_voucher

    release_order_voucher(order=order)


@transaction.atomic
def cancel_customer_order(*, user: User, order: Order) -> Order:
    order = Order.objects.select_for_update().get(pk=order.pk, user=user)
    if order.status != Order.Status.PENDING_CONFIRMATION:
        raise OrderCancellationError("Đơn hàng không còn ở trạng thái cho phép khách tự hủy.")
    if (
        order.payment_method == Order.PaymentMethod.VNPAY
        and order.payment_status == Order.PaymentStatus.PAID
    ):
        raise OrderCancellationError("Đơn VNPay đã thanh toán cần quy trình hoàn tiền riêng.")
    release_order_inventory(
        order=order,
        actor=user,
        reason=f"Khách hủy đơn {order.number}",
    )
    if order.payment_method == Order.PaymentMethod.VNPAY:
        Payment.objects.filter(order=order).update(
            status=Order.PaymentStatus.CANCELLED,
            updated_at=timezone.now(),
        )
        PaymentAttempt.objects.filter(
            payment__order=order,
            status=PaymentAttempt.Status.PENDING,
        ).update(status=PaymentAttempt.Status.CANCELLED, updated_at=timezone.now())
    previous_status = order.status
    order.status = Order.Status.CANCELLED
    order.payment_status = Order.PaymentStatus.CANCELLED
    order.cancelled_at = timezone.now()
    order.save(update_fields=["status", "payment_status", "cancelled_at", "updated_at"])
    OrderStatusHistory.objects.create(
        order=order,
        from_status=previous_status,
        to_status=Order.Status.CANCELLED,
        actor=user,
        note="Khách hàng tự hủy đơn",
    )
    return order


@transaction.atomic
def confirm_customer_received(*, user: User, order_id: int) -> Order:
    order = Order.objects.select_for_update().get(pk=order_id, user=user)
    if order.status != Order.Status.SHIPPED:
        raise OrderReceiptConfirmationError("Chỉ có thể xác nhận khi đơn hàng đang giao.")
    if (
        order.payment_method == Order.PaymentMethod.VNPAY
        and order.payment_status != Order.PaymentStatus.PAID
    ):
        raise OrderReceiptConfirmationError("Đơn VNPay chưa được xác nhận thanh toán.")

    previous_status = order.status
    order.status = Order.Status.COMPLETED
    if order.payment_method == Order.PaymentMethod.COD:
        order.payment_status = Order.PaymentStatus.PAID
    order.save(update_fields=["status", "payment_status", "updated_at"])
    OrderStatusHistory.objects.create(
        order=order,
        from_status=previous_status,
        to_status=Order.Status.COMPLETED,
        actor=user,
        note="Khách hàng xác nhận đã nhận hàng",
    )
    from apps.accounts.services import award_order_loyalty_points

    award_order_loyalty_points(order=order)
    record_order_purchase_events(order=order)
    return order


def record_order_purchase_events(*, order: Order) -> None:
    ProductEvent.objects.bulk_create(
        [
            ProductEvent(
                client_event_id=uuid.uuid4(),
                schema_version=1,
                event_type=ProductEvent.EventType.PURCHASE,
                source=ProductEvent.Source.STOREFRONT,
                product_id=item.variant.product_id,
                user=order.user,
                recommendation_context_id=(
                    ProductEvent.objects.filter(
                        user=order.user,
                        product_id=item.variant.product_id,
                        event_type=ProductEvent.EventType.ADD_CART,
                        recommendation_context_id__isnull=False,
                        created_at__gte=timezone.now() - timedelta(days=7),
                    )
                    .order_by("-created_at")
                    .values_list("recommendation_context_id", flat=True)
                    .first()
                ),
            )
            for item in order.items.select_related("variant__product")
        ]
    )
