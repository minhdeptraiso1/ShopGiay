from collections.abc import Mapping
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from .models import (
    Brand,
    Category,
    Color,
    InventoryBalance,
    InventoryReceipt,
    InventoryReceiptLine,
    Product,
    ProductEvent,
    ProductImage,
    ProductVariant,
    Size,
    StockMovement,
)

User = get_user_model()


class InsufficientStockError(Exception):
    pass


class DuplicateEventError(Exception):
    pass


def _apply_updates(instance: Any, data: Mapping[str, Any]) -> Any:
    for field, value in data.items():
        setattr(instance, field, value)
    instance.full_clean()
    instance.save()
    return instance


def create_category(*, data: Mapping[str, Any]) -> Category:
    category = Category(**data)
    category.full_clean()
    category.save()
    return category


def update_category(*, category: Category, data: Mapping[str, Any]) -> Category:
    return _apply_updates(category, data)


def deactivate_category(*, category: Category) -> Category:
    category.is_active = False
    category.save(update_fields=["is_active", "updated_at"])
    return category


def create_brand(*, data: Mapping[str, Any]) -> Brand:
    brand = Brand(**data)
    brand.full_clean()
    brand.save()
    return brand


def update_brand(*, brand: Brand, data: Mapping[str, Any]) -> Brand:
    return _apply_updates(brand, data)


def deactivate_brand(*, brand: Brand) -> Brand:
    brand.is_active = False
    brand.save(update_fields=["is_active", "updated_at"])
    return brand


def create_product(*, data: Mapping[str, Any]) -> Product:
    product = Product(**data)
    if product.status == Product.Status.PUBLISHED and not product.published_at:
        product.published_at = timezone.now()
    product.full_clean()
    product.save()
    return product


def update_product(*, product: Product, data: Mapping[str, Any]) -> Product:
    for field, value in data.items():
        setattr(product, field, value)
    if product.status == Product.Status.PUBLISHED and not product.published_at:
        product.published_at = timezone.now()
    product.full_clean()
    product.save()
    return product


def deactivate_product(*, product: Product) -> Product:
    product.status = Product.Status.INACTIVE
    product.save(update_fields=["status", "updated_at"])
    return product


def create_size(*, data: Mapping[str, Any]) -> Size:
    size = Size(**data)
    size.full_clean()
    size.save()
    return size


def update_size(*, size: Size, data: Mapping[str, Any]) -> Size:
    return _apply_updates(size, data)


def deactivate_size(*, size: Size) -> Size:
    size.is_active = False
    size.save(update_fields=["is_active"])
    return size


def create_color(*, data: Mapping[str, Any]) -> Color:
    color = Color(**data)
    color.full_clean()
    color.save()
    return color


def update_color(*, color: Color, data: Mapping[str, Any]) -> Color:
    return _apply_updates(color, data)


def deactivate_color(*, color: Color) -> Color:
    color.is_active = False
    color.save(update_fields=["is_active"])
    return color


@transaction.atomic
def create_variant(*, data: Mapping[str, Any]) -> ProductVariant:
    variant = ProductVariant(**data)
    variant.full_clean()
    variant.save()
    InventoryBalance.objects.create(variant=variant, quantity=0)
    return variant


def update_variant(*, variant: ProductVariant, data: Mapping[str, Any]) -> ProductVariant:
    return _apply_updates(variant, data)


def deactivate_variant(*, variant: ProductVariant) -> ProductVariant:
    variant.is_active = False
    variant.save(update_fields=["is_active", "updated_at"])
    return variant


@transaction.atomic
def create_product_image(*, data: Mapping[str, Any]) -> ProductImage:
    image = ProductImage(**data)
    if image.is_primary:
        ProductImage.objects.filter(product=image.product, is_primary=True).update(is_primary=False)
    image.full_clean()
    image.save()
    return image


@transaction.atomic
def update_product_image(*, image: ProductImage, data: Mapping[str, Any]) -> ProductImage:
    for field, value in data.items():
        setattr(image, field, value)
    image.full_clean(exclude=["is_primary"] if image.is_primary else None)
    if image.is_primary:
        ProductImage.objects.filter(product=image.product, is_primary=True).exclude(
            pk=image.pk
        ).update(is_primary=False)
    image.save()
    return image


@transaction.atomic
def delete_product_image(*, image: ProductImage) -> None:
    storage = image.image.storage if image.image else None
    image_name = image.image.name if image.image else ""
    image.delete()
    if storage and image_name:
        transaction.on_commit(lambda: storage.delete(image_name))


@transaction.atomic
def adjust_inventory(
    *,
    variant_id: int,
    delta: int,
    kind: str,
    reason: str,
    actor: User,
) -> StockMovement:
    variant = ProductVariant.objects.select_for_update().get(pk=variant_id)
    balance, _ = InventoryBalance.objects.select_for_update().get_or_create(variant=variant)
    quantity_after = balance.quantity + delta
    if quantity_after < 0:
        raise InsufficientStockError("Số lượng điều chỉnh làm tồn kho âm.")
    quantity_before = balance.quantity
    balance.quantity = quantity_after
    balance.save(update_fields=["quantity", "updated_at"])
    return StockMovement.objects.create(
        variant=variant,
        kind=kind,
        delta=delta,
        quantity_before=quantity_before,
        quantity_after=quantity_after,
        reason=reason,
        actor=actor,
    )


@transaction.atomic
def receive_inventory(
    *,
    lines: list[Mapping[str, Any]],
    received_at: date,
    supplier: str,
    note: str,
    actor: User,
) -> InventoryReceipt:
    """Nhập kho và cập nhật giá vốn bình quân trong cùng một transaction."""
    variant_ids = sorted({int(line["variant_id"]) for line in lines})
    variants = {
        item.id: item
        for item in ProductVariant.objects.select_for_update().filter(id__in=variant_ids)
    }
    if len(variants) != len(variant_ids):
        raise ProductVariant.DoesNotExist("Có SKU không tồn tại.")
    balances = {
        item.variant_id: item
        for item in InventoryBalance.objects.select_for_update().filter(variant_id__in=variant_ids)
    }
    receipt = InventoryReceipt.objects.create(
        received_at=received_at,
        supplier=supplier.strip(),
        note=note.strip(),
        actor=actor,
    )
    for line in lines:
        variant_id = int(line["variant_id"])
        quantity = int(line["quantity"])
        unit_cost = Decimal(line["unit_cost"])
        variant = variants[variant_id]
        balance = balances.get(variant_id)
        if balance is None:
            balance = InventoryBalance.objects.create(variant=variant)
            balances[variant_id] = balance
        quantity_before = balance.quantity
        quantity_after = quantity_before + quantity
        inventory_value = balance.average_unit_cost * quantity_before + unit_cost * quantity
        balance.quantity = quantity_after
        balance.average_unit_cost = (inventory_value / quantity_after).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
        balance.save(update_fields=["quantity", "average_unit_cost", "updated_at"])
        movement = StockMovement.objects.create(
            variant=variant,
            kind=StockMovement.Kind.RECEIPT,
            delta=quantity,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            reason=f"Nhập kho theo phiếu #{receipt.id}",
            actor=actor,
        )
        InventoryReceiptLine.objects.create(
            receipt=receipt,
            variant=variant,
            quantity=quantity,
            unit_cost=unit_cost,
            movement=movement,
        )
    from apps.notifications.models import Notification
    from apps.notifications.services import notify_staff

    notify_staff(
        kind=Notification.Kind.INVENTORY,
        title="Kho vừa được cập nhật",
        message=f"Phiếu nhập #{receipt.id} đã thêm {len(lines)} SKU vào kho.",
        link="/admin/inventory",
        payload={"receipt_id": receipt.id},
    )
    return receipt


def record_product_event(
    *,
    data: Mapping[str, Any],
    user: User | None,
) -> tuple[ProductEvent, bool]:
    try:
        defaults = {key: value for key, value in data.items() if key != "client_event_id"}
        event, created = ProductEvent.objects.get_or_create(
            client_event_id=data["client_event_id"],
            defaults={**defaults, "user": user},
        )
    except IntegrityError as exc:
        raise DuplicateEventError from exc
    return event, created
