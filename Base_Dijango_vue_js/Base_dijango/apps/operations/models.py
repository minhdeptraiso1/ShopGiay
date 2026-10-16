from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATED = "created", "Tạo mới"
        UPDATED = "updated", "Cập nhật"
        DEACTIVATED = "deactivated", "Vô hiệu hóa"
        TRANSITIONED = "transitioned", "Chuyển trạng thái"
        ADJUSTED = "adjusted", "Điều chỉnh"
        ROLE_CHANGED = "role_changed", "Đổi vai trò"

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=24, choices=Action.choices)
    entity_type = models.CharField(max_length=80, db_index=True)
    entity_id = models.CharField(max_length=64, db_index=True)
    summary = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)
    request_id = models.CharField(max_length=64, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-created_at", "-id")
        indexes = [models.Index(fields=("entity_type", "-created_at"))]

    def __str__(self) -> str:
        return f"{self.entity_type}:{self.entity_id}:{self.action}"

    def save(self, *args, **kwargs) -> None:
        if self.pk:
            raise ValidationError("Audit log là lịch sử bất biến và không thể sửa.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError("Audit log là lịch sử bất biến và không thể xóa.")
