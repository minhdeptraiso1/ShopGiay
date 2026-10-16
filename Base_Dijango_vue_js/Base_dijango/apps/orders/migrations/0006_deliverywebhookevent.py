# Generated manually for the Phase 9 delivery webhook integration.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0005_remove_orderitem_orders_item_amounts_gte_0_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="DeliveryWebhookEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("event_id", models.CharField(max_length=100, unique=True)),
                ("provider", models.CharField(max_length=50)),
                ("delivery_status", models.CharField(max_length=24)),
                ("payload_hash", models.CharField(max_length=64)),
                ("tracking_code", models.CharField(blank=True, max_length=100)),
                ("received_at", models.DateTimeField(auto_now_add=True)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="delivery_webhook_events",
                        to="orders.order",
                    ),
                ),
            ],
            options={"ordering": ["-received_at", "-id"]},
        ),
    ]
