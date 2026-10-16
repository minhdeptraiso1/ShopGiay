from collections.abc import Callable

from django.http import HttpRequest, HttpResponse

from .context import clear_audit_context, set_audit_context


class AuditContextMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        actor_id = request.user.pk if getattr(request.user, "is_authenticated", False) else None
        set_audit_context(actor_id=actor_id, request_id=getattr(request, "request_id", ""))
        try:
            return self.get_response(request)
        finally:
            clear_audit_context()
