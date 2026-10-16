from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers

from apps.accounts.roles import get_business_roles
from apps.operations.models import AuditLog

User = get_user_model()


class ReportRangeInputSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    timezone = serializers.CharField(required=False, default="Asia/Ho_Chi_Minh", max_length=64)

    def validate_timezone(self, value: str) -> str:
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise serializers.ValidationError("Múi giờ không hợp lệ.") from exc
        return value

    def validate(self, attrs):
        today = timezone.localdate()
        end_date = attrs.get("end_date", today)
        start_date = attrs.get("start_date", end_date - timedelta(days=6))
        if start_date > end_date:
            raise serializers.ValidationError({"end_date": "Ngày kết thúc phải sau ngày bắt đầu."})
        if (end_date - start_date).days > 365:
            raise serializers.ValidationError("Khoảng báo cáo tối đa là 366 ngày.")
        zone = ZoneInfo(attrs["timezone"])
        attrs["start"] = datetime.combine(start_date, time.min, tzinfo=zone)
        attrs["end"] = datetime.combine(end_date + timedelta(days=1), time.min, tzinfo=zone)
        attrs["start_date"] = start_date
        attrs["end_date"] = end_date
        return attrs


class ReportOutputSerializer(serializers.Serializer):
    pass


class StaffOutputSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "full_name", "is_active", "date_joined", "last_login", "roles")
        read_only_fields = fields

    def get_roles(self, user) -> list[str]:
        return get_business_roles(user)


class CreateStaffInputSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    full_name = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value: str) -> str:
        normalized = User.objects.normalize_email_address(value)
        if User.objects.filter(email=normalized).exists():
            raise serializers.ValidationError("Email này đã được sử dụng.")
        return normalized


class UpdateStaffInputSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255, required=False)
    is_active = serializers.BooleanField(required=False)

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError("Cần ít nhất một trường để cập nhật.")
        return attrs


class AuditLogOutputSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", allow_null=True, read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "actor",
            "actor_email",
            "action",
            "entity_type",
            "entity_id",
            "summary",
            "metadata",
            "request_id",
            "created_at",
        )
        read_only_fields = fields


class AuditLogFilterSerializer(serializers.Serializer):
    search = serializers.CharField(max_length=180, required=False, allow_blank=True)
    action = serializers.ChoiceField(choices=AuditLog.Action.choices, required=False)
    entity_type = serializers.CharField(max_length=80, required=False)
    actor_email = serializers.EmailField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
