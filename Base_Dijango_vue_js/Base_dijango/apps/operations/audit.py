from django.db.models import Model

from .context import get_audit_context
from .models import AuditLog


def record_audit(
    *,
    instance: Model,
    action: str,
    summary: str,
    metadata: dict | None = None,
) -> AuditLog:
    actor_id, request_id = get_audit_context()
    return AuditLog.objects.create(
        actor_id=actor_id,
        action=action,
        entity_type=instance._meta.label_lower,
        entity_id=str(instance.pk),
        summary=summary[:255],
        metadata=metadata or {},
        request_id=request_id,
    )
