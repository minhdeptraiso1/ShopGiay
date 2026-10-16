import secrets

from django.core.cache import cache
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import Notification
from ..services import mark_notification_read
from .serializers import (
    EmptySerializer,
    NotificationOutputSerializer,
    NotificationSummarySerializer,
    WebSocketTicketSerializer,
)


class NotificationListView(ListAPIView):
    serializer_class = NotificationOutputSerializer

    def get_queryset(self):
        queryset = Notification.objects.filter(user=self.request.user)
        if self.request.query_params.get("unread") == "true":
            queryset = queryset.filter(read_at__isnull=True)
        return queryset


class NotificationSummaryView(APIView):
    @extend_schema(responses={200: NotificationSummarySerializer})
    def get(self, request):
        return Response(
            {
                "unread_count": Notification.objects.filter(
                    user=request.user, read_at__isnull=True
                ).count()
            }
        )


class NotificationReadView(APIView):
    @extend_schema(request=EmptySerializer, responses={200: NotificationOutputSerializer})
    def post(self, request, notification_id: int):
        notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
        mark_notification_read(notification=notification)
        return Response(NotificationOutputSerializer(notification).data)


class NotificationReadAllView(APIView):
    @extend_schema(request=EmptySerializer, responses={204: None})
    def post(self, request):
        Notification.objects.filter(user=request.user, read_at__isnull=True).update(
            read_at=timezone.now()
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class WebSocketTicketView(APIView):
    @extend_schema(request=EmptySerializer, responses={201: WebSocketTicketSerializer})
    def post(self, request):
        ticket = secrets.token_urlsafe(32)
        cache.set(f"ws-ticket:{ticket}", request.user.id, timeout=60)
        return Response({"ticket": ticket, "expires_in": 60}, status=status.HTTP_201_CREATED)
