from urllib.parse import parse_qs

from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache


class WebSocketTicketAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get("query_string", b"").decode())
        ticket = query.get("ticket", [""])[0]
        user = AnonymousUser()
        if ticket:
            user_id = await sync_to_async(cache.get)(f"ws-ticket:{ticket}")
            if user_id:
                await sync_to_async(cache.delete)(f"ws-ticket:{ticket}")
                from django.contrib.auth import get_user_model

                user = await sync_to_async(get_user_model().objects.filter(pk=user_id).first)()
                user = user or AnonymousUser()
        scope["user"] = user
        return await self.app(scope, receive, send)
