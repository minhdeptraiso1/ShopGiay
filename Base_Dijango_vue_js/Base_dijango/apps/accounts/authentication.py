from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class ActiveUserJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            from apps.operations.context import set_audit_context

            user, _ = result
            set_audit_context(
                actor_id=user.pk,
                request_id=getattr(request, "request_id", ""),
            )
        return result

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not user.is_active:
            raise AuthenticationFailed("Tài khoản không hoạt động.", code="user_inactive")
        return user


class ActiveUserJWTScheme(SimpleJWTScheme):
    target_class = "apps.accounts.authentication.ActiveUserJWTAuthentication"
