from rest_framework import serializers

from ..models import Notification


class NotificationOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "kind", "title", "message", "link", "payload", "read_at", "created_at")
        read_only_fields = fields


class EmptySerializer(serializers.Serializer):
    pass


class NotificationSummarySerializer(serializers.Serializer):
    unread_count = serializers.IntegerField(min_value=0)


class WebSocketTicketSerializer(serializers.Serializer):
    ticket = serializers.CharField()
    expires_in = serializers.IntegerField(min_value=1)
