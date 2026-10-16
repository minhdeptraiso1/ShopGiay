from django.db import migrations
from django.utils import timezone


def seed_existing_data_audit(apps, schema_editor):
    AuditLog = apps.get_model("operations", "AuditLog")
    if AuditLog.objects.exists():
        return

    tracked_models = (
        ("catalog", "Category"),
        ("catalog", "Brand"),
        ("catalog", "Size"),
        ("catalog", "Color"),
        ("catalog", "Product"),
        ("catalog", "ProductVariant"),
        ("catalog", "ProductImage"),
        ("orders", "Order"),
        ("engagement", "Voucher"),
        ("engagement", "Banner"),
        ("exchanges", "ExchangeRequest"),
    )
    now = timezone.now()
    rows = []
    for app_label, model_name in tracked_models:
        model = apps.get_model(app_label, model_name)
        entity_type = f"{app_label}.{model._meta.model_name}"
        for entity_id in model.objects.values_list("pk", flat=True).iterator():
            rows.append(
                AuditLog(
                    action="created",
                    entity_type=entity_type,
                    entity_id=str(entity_id),
                    summary=f"{model._meta.verbose_name} {entity_id} đã tồn tại khi bật nhật ký.",
                    metadata={"baseline": True},
                    request_id="",
                    created_at=now,
                )
            )

    StockMovement = apps.get_model("catalog", "StockMovement")
    for movement in StockMovement.objects.values("pk", "variant_id", "delta", "kind").iterator():
        rows.append(
            AuditLog(
                action="adjusted",
                entity_type="catalog.stockmovement",
                entity_id=str(movement["pk"]),
                summary=(
                    f"SKU {movement['variant_id']} đã thay đổi tồn "
                    f"{movement['delta']:+d} trước khi bật nhật ký."
                ),
                metadata={
                    "baseline": True,
                    "kind": movement["kind"],
                    "delta": movement["delta"],
                },
                request_id="",
                created_at=now,
            )
        )

    AuditLog.objects.bulk_create(rows, batch_size=500)


class Migration(migrations.Migration):
    dependencies = [
        ("operations", "0001_initial"),
        ("catalog", "0008_inventoryreceipt_inventoryreceiptline_and_more"),
        ("engagement", "0002_voucher_required_points"),
        ("exchanges", "0002_replacement_shipped_status"),
        ("orders", "0005_remove_orderitem_orders_item_amounts_gte_0_and_more"),
    ]

    operations = [migrations.RunPython(seed_existing_data_audit, migrations.RunPython.noop)]
