import logging
from collections.abc import Iterable

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Notification

User = get_user_model()
logger = logging.getLogger(__name__)


def _group_name(user_id: int) -> str:
    return f"user_{user_id}"


def _send(*, user_id: int, event: str, payload: dict) -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    try:
        async_to_sync(channel_layer.group_send)(
            _group_name(user_id),
            {"type": "realtime.event", "event": event, "payload": payload},
        )
    except Exception:
        logger.warning("Không thể phát sự kiện realtime cho người dùng %s", user_id, exc_info=True)


def broadcast_event(*, user_ids: Iterable[int], event: str, payload: dict) -> None:
    ids = set(user_ids)
    transaction.on_commit(
        lambda: [_send(user_id=user_id, event=event, payload=payload) for user_id in ids]
    )


def create_notification(
    *,
    user_id: int,
    kind: str,
    title: str,
    message: str,
    link: str = "",
    payload: dict | None = None,
) -> Notification:
    notification = Notification.objects.create(
        user_id=user_id,
        kind=kind,
        title=title,
        message=message,
        link=link,
        payload=payload or {},
    )
    transaction.on_commit(
        lambda: _send(
            user_id=user_id,
            event="notification.created",
            payload={
                "id": notification.id,
                "kind": notification.kind,
                "title": notification.title,
                "message": notification.message,
                "link": notification.link,
                "payload": notification.payload,
                "read_at": None,
                "created_at": notification.created_at.isoformat(),
            },
        )
    )
    return notification


def notify_staff(*, kind: str, title: str, message: str, link: str, payload: dict) -> None:
    staff_ids = (
        User.objects.filter(
            Q(groups__name__in=("STAFF", "ADMIN")) | Q(is_superuser=True), is_active=True
        )
        .values_list("id", flat=True)
        .distinct()
    )
    for user_id in staff_ids:
        create_notification(
            user_id=user_id,
            kind=kind,
            title=title,
            message=message,
            link=link,
            payload=payload,
        )


def mark_notification_read(*, notification: Notification) -> Notification:
    if notification.read_at is None:
        notification.read_at = timezone.now()
        notification.save(update_fields=["read_at"])
    return notification
