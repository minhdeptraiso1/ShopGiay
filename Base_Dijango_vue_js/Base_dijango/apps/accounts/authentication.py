from drf_spectacular.contrib.rest_framework_simplejwt import SimpleJWTScheme
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class ActiveUserJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not user.is_active:
            raise AuthenticationFailed("Tài khoản không hoạt động.", code="user_inactive")
        return user


class ActiveUserJWTScheme(SimpleJWTScheme):
    target_class = "apps.accounts.authentication.ActiveUserJWTAuthentication"
