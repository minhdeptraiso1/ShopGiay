import contextvars

_audit_actor_id = contextvars.ContextVar("audit_actor_id", default=None)
_audit_request_id = contextvars.ContextVar("audit_request_id", default="")


def set_audit_context(*, actor_id: int | None, request_id: str = "") -> None:
    _audit_actor_id.set(actor_id)
    _audit_request_id.set(request_id[:64])


def clear_audit_context() -> None:
    _audit_actor_id.set(None)
    _audit_request_id.set("")


def get_audit_context() -> tuple[int | None, str]:
    return _audit_actor_id.get(), _audit_request_id.get()
