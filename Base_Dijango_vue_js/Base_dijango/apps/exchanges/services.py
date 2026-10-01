import hashlib
import json
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from apps.catalog.models import InventoryBalance, ProductVariant, StockMovement
from apps.orders.models import Order, OrderItem

from .models import ExchangeItem, ExchangeRequest, ExchangeReservation, ExchangeStatusHistory

User = get_user_model()
TERMINAL_STATUSES = (
    ExchangeRequest.Status.COMPLETED,
    ExchangeRequest.Status.REJECTED,
    ExchangeRequest.Status.CANCELLED,
)


class ExchangeError(Exception):
    pass


class ExchangeConflictError(ExchangeError):
    pass


def _history(*, exchange: ExchangeRequest, actor: User | None, old: str, note: str = "") -> None:
    ExchangeStatusHistory.objects.create(
        exchange=exchange,
        from_status=old,
        to_status=exchange.status,
        actor=actor,
        note=note.strip(),
    )


def _move_stock(*, variant_id: int, delta: int, kind: str, reason: str, actor: User | None) -> None:
    balance = InventoryBalance.objects.select_for_update().get(variant_id=variant_id)
    after = balance.quantity + delta
    if after < 0:
        raise ExchangeConflictError("Biến thể thay thế không đủ tồn kho.")
    before = balance.quantity
    balance.quantity = after
    balance.save(update_fields=["quantity", "updated_at"])
    StockMovement.objects.create(
        variant_id=variant_id,
        kind=kind,
        delta=delta,
        quantity_before=before,
        quantity_after=after,
        reason=reason,
        actor=actor,
    )


@transaction.atomic
def create_exchange(
    *,
    user: User,
    order_id: int,
    idempotency_key: uuid.UUID,
    reason: str,
    evidence_url: str,
    customer_note: str,
    items: list[dict],
) -> tuple[ExchangeRequest, bool]:
    fingerprint_payload = {
        "order_id": order_id,
        "reason": reason.strip(),
        "evidence_url": evidence_url.strip(),
        "customer_note": customer_note.strip(),
        "items": sorted(items, key=lambda row: row["order_item_id"]),
    }
    request_fingerprint = hashlib.sha256(
        json.dumps(fingerprint_payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    existing = ExchangeRequest.objects.filter(user=user, idempotency_key=idempotency_key).first()
    if existing:
        if existing.request_fingerprint != request_fingerprint:
            raise ExchangeConflictError(
                "Idempotency-Key đã được dùng cho một yêu cầu đổi hàng khác."
            )
        return existing, False
    order = Order.objects.select_for_update().get(pk=order_id, user=user)
    if order.status != Order.Status.COMPLETED:
        raise ExchangeError("Chỉ đơn hàng đã hoàn tất mới được yêu cầu đổi.")
    completed_at = (
        order.status_history.filter(to_status=Order.Status.COMPLETED)
        .order_by("-created_at")
        .values_list("created_at", flat=True)
        .first()
    )
    if not completed_at or completed_at < timezone.now() - timedelta(
        days=settings.EXCHANGE_WINDOW_DAYS
    ):
        raise ExchangeError("Đơn hàng đã hết thời hạn đổi hàng.")
    if not items:
        raise ExchangeError("Yêu cầu đổi phải có ít nhất một sản phẩm.")

    order_items = {
        item.id: item
        for item in OrderItem.objects.select_for_update()
        .select_related("variant__product")
        .filter(order=order, id__in=[row["order_item_id"] for row in items])
    }
    targets = {
        variant.id: variant
        for variant in ProductVariant.objects.select_related("product", "size", "color").filter(
            id__in=[row["target_variant_id"] for row in items], is_active=True
        )
    }
    if len(order_items) != len(items) or any(
        row["target_variant_id"] not in targets for row in items
    ):
        raise ExchangeError("Sản phẩm hoặc biến thể đổi không hợp lệ.")

    exchange = ExchangeRequest.objects.create(
        user=user,
        order=order,
        idempotency_key=idempotency_key,
        request_fingerprint=request_fingerprint,
        reason=reason.strip(),
        evidence_url=evidence_url.strip(),
        customer_note=customer_note.strip(),
    )
    for row in items:
        order_item = order_items[row["order_item_id"]]
        target = targets[row["target_variant_id"]]
        quantity = row["quantity"]
        if target.product_id != order_item.variant.product_id or target.id == order_item.variant_id:
            raise ExchangeError("Chỉ được đổi size/màu khác trong cùng sản phẩm.")
        already_requested = (
            ExchangeItem.objects.filter(order_item=order_item)
            .exclude(
                exchange__status__in=(
                    ExchangeRequest.Status.REJECTED,
                    ExchangeRequest.Status.CANCELLED,
                )
            )
            .aggregate(total=Sum("quantity"))["total"]
            or 0
        )
        if quantity < 1 or already_requested + quantity > order_item.quantity:
            raise ExchangeError("Số lượng đổi vượt quá số lượng còn đủ điều kiện.")
        ExchangeItem.objects.create(
            exchange=exchange,
            order_item=order_item,
            target_variant=target,
            quantity=quantity,
        )
    _history(exchange=exchange, actor=user, old="", note="Khách hàng tạo yêu cầu đổi hàng")
    return exchange, True


@transaction.atomic
def cancel_customer_exchange(*, user: User, exchange_id: int) -> ExchangeRequest:
    exchange = ExchangeRequest.objects.select_for_update().get(pk=exchange_id, user=user)
    if exchange.status != ExchangeRequest.Status.PENDING:
        raise ExchangeConflictError("Chỉ yêu cầu đang chờ duyệt mới có thể hủy.")
    old = exchange.status
    exchange.status = ExchangeRequest.Status.CANCELLED
    exchange.save(update_fields=["status", "updated_at"])
    _history(exchange=exchange, actor=user, old=old, note="Khách hàng hủy yêu cầu")
    return exchange


def _release_reservations(*, exchange: ExchangeRequest, actor: User | None, reason: str) -> None:
    reservations = list(
        ExchangeReservation.objects.select_for_update()
        .select_related("variant")
        .filter(exchange_item__exchange=exchange, status=ExchangeReservation.Status.ACTIVE)
        .order_by("variant_id")
    )
    for reservation in reservations:
        _move_stock(
            variant_id=reservation.variant_id,
            delta=reservation.quantity,
            kind=StockMovement.Kind.EXCHANGE_RELEASE,
            reason=reason,
            actor=actor,
        )
        reservation.status = ExchangeReservation.Status.RELEASED
        reservation.released_at = timezone.now()
        reservation.save(update_fields=["status", "released_at", "updated_at"])


@transaction.atomic
def transition_exchange(
    *,
    exchange_id: int,
    actor: User,
    action: str,
    expected_updated_at,
    note: str = "",
    item_updates: list[dict] | None = None,
    tracking_number: str = "",
) -> ExchangeRequest:
    exchange = ExchangeRequest.objects.select_for_update().get(pk=exchange_id)
    if exchange.updated_at != expected_updated_at:
        raise ExchangeConflictError("Yêu cầu đã được cập nhật. Hãy tải lại dữ liệu.")
    old = exchange.status
    items = list(exchange.items.select_related("order_item", "target_variant").order_by("id"))
    updates = {row["item_id"]: row for row in item_updates or []}

    if action == "approve" and old == ExchangeRequest.Status.PENDING:
        expires_at = timezone.now() + timedelta(minutes=settings.EXCHANGE_RESERVATION_MINUTES)
        for item in sorted(items, key=lambda row: row.target_variant_id):
            _move_stock(
                variant_id=item.target_variant_id,
                delta=-item.quantity,
                kind=StockMovement.Kind.EXCHANGE_RESERVATION,
                reason=f"Giữ hàng đổi cho yêu cầu EX-{exchange.id}",
                actor=actor,
            )
            ExchangeReservation.objects.create(
                exchange_item=item,
                variant=item.target_variant,
                quantity=item.quantity,
                expires_at=expires_at,
            )
        exchange.status = ExchangeRequest.Status.APPROVED
        exchange.approved_by = actor
        exchange.reservation_expires_at = expires_at
    elif action == "reject" and old in (
        ExchangeRequest.Status.PENDING,
        ExchangeRequest.Status.APPROVED,
    ):
        if old == ExchangeRequest.Status.APPROVED:
            _release_reservations(
                exchange=exchange, actor=actor, reason=f"Từ chối yêu cầu EX-{exchange.id}"
            )
        exchange.status = ExchangeRequest.Status.REJECTED
    elif action == "receive" and old == ExchangeRequest.Status.APPROVED:
        for item in items:
            received = updates.get(item.id, {}).get("received_quantity", item.quantity)
            if received < 0 or received > item.quantity:
                raise ExchangeError("Số lượng nhận không hợp lệ.")
            item.received_quantity = received
            item.save(update_fields=["received_quantity"])
        exchange.status = ExchangeRequest.Status.RECEIVED
    elif action == "inspect" and old == ExchangeRequest.Status.RECEIVED:
        for item in items:
            row = updates.get(item.id)
            if row is None:
                raise ExchangeError("Thiếu kết quả kiểm hàng cho sản phẩm.")
            accepted = row.get("accepted_quantity", 0)
            if accepted < 0 or accepted > item.received_quantity:
                raise ExchangeError("Số lượng đạt kiểm tra không hợp lệ.")
            disposition = row.get("disposition", ExchangeItem.Disposition.DAMAGED)
            if accepted and disposition != ExchangeItem.Disposition.RESTOCK:
                raise ExchangeError("Hàng đạt kiểm tra phải có disposition restock.")
            item.accepted_quantity = accepted
            item.disposition = disposition
            item.inspection_note = row.get("inspection_note", "").strip()
            item.save(update_fields=["accepted_quantity", "disposition", "inspection_note"])
            reservation = ExchangeReservation.objects.select_for_update().get(exchange_item=item)
            release_quantity = reservation.quantity - accepted
            if release_quantity:
                _move_stock(
                    variant_id=reservation.variant_id,
                    delta=release_quantity,
                    kind=StockMovement.Kind.EXCHANGE_RELEASE,
                    reason=f"Giảm giữ hàng sau kiểm tra EX-{exchange.id}",
                    actor=actor,
                )
            if accepted:
                reservation.quantity = accepted
            else:
                reservation.status = ExchangeReservation.Status.RELEASED
                reservation.released_at = timezone.now()
            reservation.save(update_fields=["quantity", "status", "released_at", "updated_at"])
        exchange.status = ExchangeRequest.Status.INSPECTED
    elif action == "prepare" and old == ExchangeRequest.Status.INSPECTED:
        if not any(item.accepted_quantity for item in items):
            raise ExchangeConflictError("Không có sản phẩm đạt kiểm tra để giao đổi.")
        ExchangeReservation.objects.filter(
            exchange_item__exchange=exchange, status=ExchangeReservation.Status.ACTIVE
        ).update(status=ExchangeReservation.Status.CAPTURED, updated_at=timezone.now())
        exchange.status = ExchangeRequest.Status.REPLACEMENT_READY
        exchange.tracking_number = tracking_number.strip()
    elif action == "ship" and old == ExchangeRequest.Status.REPLACEMENT_READY:
        if not tracking_number.strip() and not exchange.tracking_number:
            raise ExchangeError("Cần nhập mã vận đơn trước khi giao hàng đổi.")
        exchange.status = ExchangeRequest.Status.REPLACEMENT_SHIPPED
        exchange.tracking_number = tracking_number.strip() or exchange.tracking_number
    else:
        raise ExchangeConflictError("Thao tác không hợp lệ với trạng thái hiện tại.")

    exchange.staff_note = note.strip() or exchange.staff_note
    exchange.save()
    _history(exchange=exchange, actor=actor, old=old, note=note)
    return exchange


@transaction.atomic
def confirm_replacement_received(*, user: User, exchange_id: int) -> ExchangeRequest:
    exchange = ExchangeRequest.objects.select_for_update().get(pk=exchange_id, user=user)
    if exchange.status != ExchangeRequest.Status.REPLACEMENT_SHIPPED:
        raise ExchangeConflictError("Chỉ xác nhận khi hàng đổi đang được giao.")
    old = exchange.status
    for item in exchange.items.select_related("order_item"):
        if item.accepted_quantity:
            _move_stock(
                variant_id=item.order_item.variant_id,
                delta=item.accepted_quantity,
                kind=StockMovement.Kind.EXCHANGE_RETURN,
                reason=f"Nhập lại hàng đạt kiểm tra EX-{exchange.id}",
                actor=user,
            )
    exchange.status = ExchangeRequest.Status.COMPLETED
    exchange.save(update_fields=["status", "updated_at"])
    _history(
        exchange=exchange,
        actor=user,
        old=old,
        note="Khách hàng xác nhận đã nhận sản phẩm đổi",
    )
    return exchange


@transaction.atomic
def expire_exchange(*, exchange_id: int) -> bool:
    exchange = ExchangeRequest.objects.select_for_update().get(pk=exchange_id)
    if (
        exchange.status != ExchangeRequest.Status.APPROVED
        or not exchange.reservation_expires_at
        or exchange.reservation_expires_at > timezone.now()
    ):
        return False
    _release_reservations(
        exchange=exchange, actor=None, reason=f"Hết hạn giữ hàng đổi EX-{exchange.id}"
    )
    old = exchange.status
    exchange.status = ExchangeRequest.Status.CANCELLED
    exchange.save(update_fields=["status", "updated_at"])
    _history(exchange=exchange, actor=None, old=old, note="Hết hạn giữ biến thể thay thế")
    return True
