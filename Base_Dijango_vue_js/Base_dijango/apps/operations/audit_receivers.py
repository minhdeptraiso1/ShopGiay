from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from apps.catalog.models import (
    Brand,
    Category,
    Color,
    Product,
    ProductImage,
    ProductVariant,
    Size,
    StockMovement,
)
from apps.engagement.models import Banner, Voucher
from apps.exchanges.models import ExchangeRequest
from apps.orders.models import Order

from .audit import record_audit
from .models import AuditLog

TRACKED_MODELS = (
    Category,
    Brand,
    Size,
    Color,
    Product,
    ProductVariant,
    ProductImage,
    Order,
    Voucher,
    Banner,
    ExchangeRequest,
)


@receiver(post_save)
def audit_tracked_save(sender, instance, created: bool, **kwargs) -> None:
    if sender not in TRACKED_MODELS:
        return
    action = AuditLog.Action.CREATED if created else AuditLog.Action.UPDATED
    if sender in (Order, ExchangeRequest) and not created:
        action = AuditLog.Action.TRANSITIONED
    verb = "tạo" if created else "cập nhật"
    record_audit(
        instance=instance,
        action=action,
        summary=f"{instance._meta.verbose_name} {instance.pk} đã được {verb}.",
    )


@receiver(post_delete)
def audit_tracked_delete(sender, instance, **kwargs) -> None:
    if sender not in TRACKED_MODELS:
        return
    record_audit(
        instance=instance,
        action=AuditLog.Action.DEACTIVATED,
        summary=f"{instance._meta.verbose_name} {instance.pk} đã bị xóa hoặc vô hiệu hóa.",
    )


@receiver(post_save, sender=StockMovement)
def audit_stock_movement(sender, instance: StockMovement, created: bool, **kwargs) -> None:
    if not created:
        return
    record_audit(
        instance=instance,
        action=AuditLog.Action.ADJUSTED,
        summary=f"SKU {instance.variant_id} thay đổi tồn {instance.delta:+d}.",
        metadata={"kind": instance.kind, "delta": instance.delta},
    )


User = get_user_model()


@receiver(m2m_changed, sender=User.groups.through)
def audit_user_roles(sender, instance, action: str, pk_set, **kwargs) -> None:
    if not isinstance(instance, User) or action not in {"post_add", "post_remove", "post_clear"}:
        return
    record_audit(
        instance=instance,
        action=AuditLog.Action.ROLE_CHANGED,
        summary=f"Vai trò của tài khoản {instance.email} đã thay đổi.",
        metadata={"group_ids": sorted(pk_set or [])},
    )
