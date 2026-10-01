import hashlib
import hmac
import ipaddress
import json
import uuid
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode, urlsplit, urlunsplit

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from .models import (
    InventoryReservation,
    Order,
    OrderStatusHistory,
    Payment,
    PaymentAttempt,
    PaymentEvent,
)
from .services import release_order_inventory

User = get_user_model()


class PaymentConfigurationError(Exception):
    pass


class PaymentCreationError(Exception):
    pass


@dataclass(frozen=True)
class VnpayIpnResult:
    response_code: str
    message: str


def _signed_fields(params: dict[str, str]) -> dict[str, str]:
    return {
        key: value
        for key, value in params.items()
        if key not in {"vnp_SecureHash", "vnp_SecureHashType"} and value != ""
    }


def sign_vnpay_params(params: dict[str, str], secret: str) -> str:
    sign_data = urlencode(sorted(_signed_fields(params).items()))
    return hmac.new(secret.encode(), sign_data.encode(), hashlib.sha512).hexdigest()


def verify_vnpay_signature(params: dict[str, str]) -> bool:
    received = params.get("vnp_SecureHash", "")
    if not received or not settings.VNPAY_HASH_SECRET:
        return False
    expected = sign_vnpay_params(params, settings.VNPAY_HASH_SECRET)
    return hmac.compare_digest(received.casefold(), expected.casefold())


def _normalize_return_url(value: str) -> str:
    candidate = value.strip() or settings.VNPAY_RETURN_URL
    parsed = urlsplit(candidate)
    allowed = urlsplit(settings.FRONTEND_BASE_URL)
    if (
        parsed.scheme not in {"http", "https"}
        or parsed.scheme != allowed.scheme
        or parsed.netloc != allowed.netloc
        or parsed.username
        or parsed.password
    ):
        raise PaymentCreationError("Return URL không thuộc frontend đã cấu hình.")
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path or "/", parsed.query, ""))


def _build_vnpay_url(
    *, attempt: PaymentAttempt, ip_address: str, locale: str, bank_code: str, return_url: str
) -> str:
    try:
        normalized_ip = str(ipaddress.ip_address(ip_address))
    except ValueError:
        normalized_ip = "127.0.0.1"
    now = timezone.localtime()
    expires_at = timezone.localtime(attempt.expires_at)
    params = {
        "vnp_Version": settings.VNPAY_VERSION,
        "vnp_Command": settings.VNPAY_COMMAND,
        "vnp_TmnCode": settings.VNPAY_TMN_CODE,
        "vnp_Amount": str(int(attempt.payment.amount * 100)),
        "vnp_CurrCode": attempt.payment.currency,
        "vnp_TxnRef": attempt.reference,
        "vnp_OrderInfo": f"Thanh toan don hang {attempt.payment.order.number}",
        "vnp_OrderType": settings.VNPAY_ORDER_TYPE,
        "vnp_Locale": locale,
        "vnp_ReturnUrl": return_url,
        "vnp_IpAddr": normalized_ip,
        "vnp_CreateDate": now.strftime("%Y%m%d%H%M%S"),
        "vnp_ExpireDate": expires_at.strftime("%Y%m%d%H%M%S"),
    }
    if bank_code:
        params["vnp_BankCode"] = bank_code
    params["vnp_SecureHash"] = sign_vnpay_params(params, settings.VNPAY_HASH_SECRET)
    return f"{settings.VNPAY_PAYMENT_URL}?{urlencode(sorted(params.items()))}"


def _attempt_fingerprint(*, locale: str, bank_code: str, return_url: str) -> str:
    payload = json.dumps(
        {"bank_code": bank_code, "locale": locale, "return_url": return_url},
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


@transaction.atomic
def create_vnpay_attempt(
    *,
    user: User,
    order_id: int,
    idempotency_key: uuid.UUID,
    ip_address: str,
    locale: str = "vn",
    bank_code: str = "",
    return_url: str = "",
) -> tuple[PaymentAttempt, bool]:
    if not settings.VNPAY_TMN_CODE or not settings.VNPAY_HASH_SECRET:
        raise PaymentConfigurationError("VNPay sandbox chưa được cấu hình đầy đủ.")
    order = Order.objects.select_for_update().get(pk=order_id, user=user)
    if order.payment_method != Order.PaymentMethod.VNPAY:
        raise PaymentCreationError("Đơn hàng không chọn phương thức VNPay.")
    if order.status != Order.Status.PENDING_CONFIRMATION:
        raise PaymentCreationError("Đơn hàng không còn chờ thanh toán.")
    payment = Payment.objects.select_for_update().get(order=order)
    if payment.status != Order.PaymentStatus.PENDING:
        raise PaymentCreationError("Thanh toán không còn ở trạng thái pending.")
    normalized_return_url = _normalize_return_url(return_url)
    fingerprint = _attempt_fingerprint(
        locale=locale, bank_code=bank_code, return_url=normalized_return_url
    )
    existing = PaymentAttempt.objects.filter(
        payment=payment, idempotency_key=idempotency_key
    ).first()
    if existing:
        if existing.request_fingerprint != fingerprint:
            raise PaymentCreationError("Idempotency key đã được dùng với request khác.")
        return existing, False

    reservations = list(
        InventoryReservation.objects.select_for_update().filter(
            order_item__order=order,
            status=InventoryReservation.Status.ACTIVE,
        )
    )
    if not reservations or min(item.expires_at for item in reservations) <= timezone.now():
        raise PaymentCreationError("Thời gian giữ hàng đã hết hạn.")
    expires_at = min(item.expires_at for item in reservations)
    attempt = PaymentAttempt.objects.create(
        payment=payment,
        idempotency_key=idempotency_key,
        request_fingerprint=fingerprint,
        reference=uuid.uuid4().hex,
        expires_at=expires_at,
    )
    attempt.checkout_url = _build_vnpay_url(
        attempt=attempt,
        ip_address=ip_address,
        locale=locale,
        bank_code=bank_code,
        return_url=normalized_return_url,
    )
    attempt.save(update_fields=["checkout_url", "updated_at"])
    return attempt, True


def _event_key(params: dict[str, str]) -> str:
    canonical = urlencode(sorted((key, value) for key, value in params.items() if value != ""))
    return hashlib.sha256(canonical.encode()).hexdigest()


def _mark_payment_failed(*, attempt: PaymentAttempt, response_code: str) -> None:
    payment = attempt.payment
    order = payment.order
    attempt.status = PaymentAttempt.Status.FAILED
    attempt.response_code = response_code
    attempt.save(update_fields=["status", "response_code", "updated_at"])
    PaymentAttempt.objects.filter(
        payment=payment,
        status=PaymentAttempt.Status.PENDING,
    ).exclude(pk=attempt.pk).update(
        status=PaymentAttempt.Status.CANCELLED,
        updated_at=timezone.now(),
    )
    payment.status = Order.PaymentStatus.FAILED
    payment.save(update_fields=["status", "updated_at"])
    release_order_inventory(
        order=order,
        actor=None,
        reason=f"Hoàn giữ hàng do VNPay thất bại cho đơn {order.number}",
    )
    previous_status = order.status
    order.status = Order.Status.CANCELLED
    order.payment_status = Order.PaymentStatus.FAILED
    order.cancelled_at = timezone.now()
    order.save(update_fields=["status", "payment_status", "cancelled_at", "updated_at"])
    OrderStatusHistory.objects.create(
        order=order,
        from_status=previous_status,
        to_status=Order.Status.CANCELLED,
        note=f"VNPay thất bại, response code {response_code}",
    )


@transaction.atomic
def process_vnpay_ipn(*, params: dict[str, str]) -> VnpayIpnResult:
    reference = params.get("vnp_TxnRef", "")
    try:
        attempt = (
            PaymentAttempt.objects.select_for_update()
            .select_related("payment__order")
            .get(reference=reference)
        )
    except PaymentAttempt.DoesNotExist:
        return VnpayIpnResult("01", "Order not found")

    payment = attempt.payment
    order = payment.order
    event_key = _event_key(params)
    if PaymentEvent.objects.filter(event_key=event_key).exists():
        return VnpayIpnResult("02", "Order already confirmed")

    signature_valid = verify_vnpay_signature(params)
    event = PaymentEvent.objects.create(
        payment=payment,
        attempt=attempt,
        provider=Payment.Provider.VNPAY,
        event_key=event_key,
        response_code=params.get("vnp_ResponseCode", ""),
        transaction_status=params.get("vnp_TransactionStatus", ""),
        signature_valid=signature_valid,
        outcome="received",
    )
    if not signature_valid or params.get("vnp_TmnCode") != settings.VNPAY_TMN_CODE:
        event.outcome = "invalid_signature"
        event.processed_at = timezone.now()
        event.save(update_fields=["outcome", "processed_at"])
        return VnpayIpnResult("97", "Invalid signature")

    try:
        received_amount = Decimal(params.get("vnp_Amount", "")) / 100
    except (InvalidOperation, ValueError):
        received_amount = Decimal("-1")
    if received_amount != payment.amount:
        event.outcome = "invalid_amount"
        event.processed_at = timezone.now()
        event.save(update_fields=["outcome", "processed_at"])
        return VnpayIpnResult("04", "Invalid amount")
    if payment.status == Order.PaymentStatus.PAID:
        event.outcome = "already_paid"
        event.processed_at = timezone.now()
        event.save(update_fields=["outcome", "processed_at"])
        return VnpayIpnResult("02", "Order already confirmed")
    if order.status == Order.Status.CANCELLED or attempt.expires_at <= timezone.now():
        event.outcome = "late_after_cancel"
        event.processed_at = timezone.now()
        event.save(update_fields=["outcome", "processed_at"])
        return VnpayIpnResult("02", "Order already confirmed")

    response_code = params.get("vnp_ResponseCode", "")
    transaction_status = params.get("vnp_TransactionStatus", "")
    if response_code != "00" or transaction_status != "00":
        _mark_payment_failed(attempt=attempt, response_code=response_code)
        event.outcome = "payment_failed"
        event.processed_at = timezone.now()
        event.save(update_fields=["outcome", "processed_at"])
        return VnpayIpnResult("00", "Confirm Success")

    transaction_no = params.get("vnp_TransactionNo", "")
    if not transaction_no:
        event.outcome = "missing_transaction_reference"
        event.processed_at = timezone.now()
        event.save(update_fields=["outcome", "processed_at"])
        return VnpayIpnResult("99", "Unknown error")
    if (
        Payment.objects.exclude(pk=payment.pk)
        .filter(
            provider=Payment.Provider.VNPAY,
            provider_transaction_no=transaction_no,
        )
        .exists()
    ):
        event.outcome = "duplicate_transaction_reference"
        event.processed_at = timezone.now()
        event.save(update_fields=["outcome", "processed_at"])
        return VnpayIpnResult("02", "Order already confirmed")

    attempt.status = PaymentAttempt.Status.SUCCEEDED
    attempt.response_code = response_code
    attempt.save(update_fields=["status", "response_code", "updated_at"])
    PaymentAttempt.objects.filter(
        payment=payment,
        status=PaymentAttempt.Status.PENDING,
    ).exclude(pk=attempt.pk).update(
        status=PaymentAttempt.Status.CANCELLED,
        updated_at=timezone.now(),
    )
    payment.status = Order.PaymentStatus.PAID
    payment.provider_transaction_no = transaction_no
    payment.paid_at = timezone.now()
    payment.save(update_fields=["status", "provider_transaction_no", "paid_at", "updated_at"])
    InventoryReservation.objects.filter(
        order_item__order=order,
        status=InventoryReservation.Status.ACTIVE,
    ).update(status=InventoryReservation.Status.CAPTURED, updated_at=timezone.now())
    from apps.engagement.services import redeem_order_voucher

    redeem_order_voucher(order=order)
    previous_status = order.status
    order.status = Order.Status.CONFIRMED
    order.payment_status = Order.PaymentStatus.PAID
    order.save(update_fields=["status", "payment_status", "updated_at"])
    OrderStatusHistory.objects.create(
        order=order,
        from_status=previous_status,
        to_status=Order.Status.CONFIRMED,
        note="VNPay IPN xác nhận thanh toán thành công",
    )
    event.outcome = "payment_succeeded"
    event.processed_at = timezone.now()
    event.save(update_fields=["outcome", "processed_at"])
    return VnpayIpnResult("00", "Confirm Success")


@transaction.atomic
def expire_order_reservations(*, order_id: int) -> bool:
    order = Order.objects.select_for_update().get(pk=order_id)
    payment = Payment.objects.select_for_update().get(order=order)
    reservations = list(
        InventoryReservation.objects.select_for_update().filter(
            order_item__order=order,
            status=InventoryReservation.Status.ACTIVE,
            expires_at__lte=timezone.now(),
        )
    )
    if not reservations or order.payment_status == Order.PaymentStatus.PAID:
        return False
    release_order_inventory(
        order=order,
        actor=None,
        reason=f"Hoàn giữ hàng hết hạn cho đơn {order.number}",
    )
    PaymentAttempt.objects.filter(payment=payment, status=PaymentAttempt.Status.PENDING).update(
        status=PaymentAttempt.Status.EXPIRED, updated_at=timezone.now()
    )
    payment.status = Order.PaymentStatus.FAILED
    payment.save(update_fields=["status", "updated_at"])
    previous_status = order.status
    order.status = Order.Status.CANCELLED
    order.payment_status = Order.PaymentStatus.FAILED
    order.cancelled_at = timezone.now()
    order.save(update_fields=["status", "payment_status", "cancelled_at", "updated_at"])
    OrderStatusHistory.objects.create(
        order=order,
        from_status=previous_status,
        to_status=Order.Status.CANCELLED,
        note="Hết thời gian giữ hàng cho thanh toán VNPay",
    )
    return True
