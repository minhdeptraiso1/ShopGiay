from django.urls import path

from .views import (
    NotificationListView,
    NotificationReadAllView,
    NotificationReadView,
    NotificationSummaryView,
    WebSocketTicketView,
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("summary/", NotificationSummaryView.as_view(), name="notification-summary"),
    path("read-all/", NotificationReadAllView.as_view(), name="notification-read-all"),
    path("<int:notification_id>/read/", NotificationReadView.as_view(), name="notification-read"),
    path("websocket-ticket/", WebSocketTicketView.as_view(), name="websocket-ticket"),
]
