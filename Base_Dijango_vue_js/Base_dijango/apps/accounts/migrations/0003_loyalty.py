import django.db.models.deletion
from decimal import ROUND_HALF_UP, Decimal
from django.conf import settings
from django.db import migrations, models


def reward_completed_orders(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    LoyaltyAccount = apps.get_model("accounts", "LoyaltyAccount")
    LoyaltyTransaction = apps.get_model("accounts", "LoyaltyTransaction")
    for order in Order.objects.filter(status="completed").iterator():
        points = int(
            (Decimal(order.total) * Decimal("0.005")).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
        if points <= 0 or LoyaltyTransaction.objects.filter(order_id=order.id).exists():
            continue
        account, _ = LoyaltyAccount.objects.get_or_create(user_id=order.user_id)
        account.balance += points
        account.save(update_fields=["balance", "updated_at"])
        LoyaltyTransaction.objects.create(
            account_id=account.id,
            order_id=order.id,
            kind="order_reward",
            points=points,
            balance_after=account.balance,
            note=f"Hoàn tất đơn {order.number}",
        )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_address"),
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoyaltyAccount",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("balance", models.PositiveBigIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="loyalty_account", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="LoyaltyTransaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("kind", models.CharField(choices=[("order_reward", "Thưởng đơn hàng"), ("adjustment", "Điều chỉnh")], max_length=24)),
                ("points", models.BigIntegerField()),
                ("balance_after", models.PositiveBigIntegerField()),
                ("note", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transactions", to="accounts.loyaltyaccount")),
                ("order", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="loyalty_reward", to="orders.order")),
            ],
            options={"ordering": ("-created_at", "-id")},
        ),
        migrations.RunPython(reward_completed_orders, migrations.RunPython.noop),
    ]
