from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0006_deliverywebhookevent"),
    ]

    operations = [
        migrations.DeleteModel(name="DeliveryWebhookEvent"),
    ]
