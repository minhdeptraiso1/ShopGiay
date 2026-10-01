from django.db import migrations, models


STATUSES = [
    ("pending", "Chờ duyệt"),
    ("approved", "Đã duyệt"),
    ("received", "Đã nhận hàng"),
    ("inspected", "Đã kiểm hàng"),
    ("replacement_ready", "Sẵn sàng giao đổi"),
    ("replacement_shipped", "Đang giao hàng đổi"),
    ("completed", "Hoàn tất"),
    ("rejected", "Từ chối"),
    ("cancelled", "Đã hủy"),
]


class Migration(migrations.Migration):
    dependencies = [("exchanges", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="exchangerequest",
            name="status",
            field=models.CharField(choices=STATUSES, db_index=True, default="pending", max_length=24),
        ),
        migrations.AlterField(
            model_name="exchangestatushistory",
            name="from_status",
            field=models.CharField(blank=True, choices=STATUSES, max_length=24),
        ),
        migrations.AlterField(
            model_name="exchangestatushistory",
            name="to_status",
            field=models.CharField(choices=STATUSES, max_length=24),
        ),
    ]
