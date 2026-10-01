from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from .models import Order, OrderStatusHistory, PaymentAttempt
from .services import release_order_inventory

User = get_user_model()


class OrderTransitionError(Exception):
    pass


class StaleOrderError(Exception):
    pass


ALLOWED_TRANSITIONS = {
    Order.Status.PENDING_CONFIRMATION: {Order.Status.CONFIRMED, Order.Status.CANCELLED},
    Order.Status.CONFIRMED: {Order.Status.PREPARING, Order.Status.CANCELLED},
    Order.Status.PREPARING: {Order.Status.SHIPPED, Order.Status.CANCELLED},
    Order.Status.SHIPPED: {Order.Status.COMPLETED},
    Order.Status.COMPLETED: set(),
    Order.Status.CANCELLED: set(),
}


@transaction.atomic
def transition_order(
    *,
    order_id: int,
    actor: User,
    to_status: str,
    expected_updated_at: datetime,
    note: str = "",
) -> Order:
    order = Order.objects.select_for_update().get(pk=order_id)
    if order.updated_at != expected_updated_at:
        raise StaleOrderError("Đơn hàng đã được cập nhật bởi thao tác khác.")
    if to_status not in ALLOWED_TRANSITIONS[order.status]:
        raise OrderTransitionError(f"Không thể chuyển đơn từ {order.status} sang {to_status}.")
    if (
        to_status == Order.Status.CONFIRMED
        and order.payment_method == Order.PaymentMethod.VNPAY
        and order.payment_status != Order.PaymentStatus.PAID
    ):
        raise OrderTransitionError("Đơn VNPay chỉ được xác nhận bởi IPN thanh toán thành công.")
    if (
        to_status == Order.Status.CANCELLED
        and order.payment_method == Order.PaymentMethod.VNPAY
        and order.payment_status == Order.PaymentStatus.PAID
    ):
        raise OrderTransitionError("Đơn VNPay đã thanh toán cần quy trình hoàn tiền riêng.")

    previous_status = order.status
    if to_status == Order.Status.CANCELLED:
        release_order_inventory(
            order=order,
            actor=actor,
            reason=f"Nhân viên hủy đơn {order.number}",
        )
        order.payment_status = Order.PaymentStatus.CANCELLED
        if hasattr(order, "payment"):
            order.payment.status = Order.PaymentStatus.CANCELLED
            order.payment.save(update_fields=["status", "updated_at"])
            order.payment.attempts.filter(status=PaymentAttempt.Status.PENDING).update(
                status=PaymentAttempt.Status.CANCELLED,
                updated_at=timezone.now(),
            )
    elif to_status == Order.Status.COMPLETED and order.payment_method == Order.PaymentMethod.COD:
        order.payment_status = Order.PaymentStatus.PAID

    order.status = to_status
    update_fields = ["status", "payment_status", "updated_at"]
    if to_status == Order.Status.CANCELLED:
        order.cancelled_at = timezone.now()
        update_fields.append("cancelled_at")
    order.save(update_fields=update_fields)
    OrderStatusHistory.objects.create(
        order=order,
        from_status=previous_status,
        to_status=to_status,
        actor=actor,
        note=note,
    )
    if to_status == Order.Status.COMPLETED:
        from apps.accounts.services import award_order_loyalty_points
        from apps.orders.services import record_order_purchase_events

        award_order_loyalty_points(order=order)
        record_order_purchase_events(order=order)
    return order
