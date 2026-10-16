from django.conf import settings
from django.db import models


class Notification(models.Model):
    class Kind(models.TextChoices):
        ORDER = "order", "Đơn hàng"
        EXCHANGE = "exchange", "Đổi hàng"
        INVENTORY = "inventory", "Kho hàng"
        SYSTEM = "system", "Hệ thống"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    kind = models.CharField(max_length=20, choices=Kind.choices, db_index=True)
    title = models.CharField(max_length=180)
    message = models.CharField(max_length=500)
    link = models.CharField(max_length=255, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    read_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["user", "read_at", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.user_id}: {self.title}"
