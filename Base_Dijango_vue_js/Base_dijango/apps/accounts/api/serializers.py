from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

User = get_user_model()


class UserOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "is_active", "date_joined")
        read_only_fields = fields


class LoginInputSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email = User.objects.normalize_email_address(attrs["email"])
        user = authenticate(
            request=self.context.get("request"), email=email, password=attrs["password"]
        )
        if user is None or not user.is_active:
            raise AuthenticationFailed(
                "Email hoặc mật khẩu không hợp lệ.", code="invalid_credentials"
            )
        attrs["user"] = user
        return attrs


class LoginOutputSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True)
    user = UserOutputSerializer(read_only=True)


class UpdateProfileInputSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255, allow_blank=True, trim_whitespace=True)


class ActiveUserTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        try:
            token = RefreshToken(attrs["refresh"])
            user_id = token.get("user_id")
        except TokenError as exc:
            raise serializers.ValidationError(
                {"refresh": "Refresh token không hợp lệ hoặc đã hết hạn."}, code="token_not_valid"
            ) from exc
        if not User.objects.filter(id=user_id, is_active=True).exists():
            raise AuthenticationFailed("Tài khoản không hoạt động.", code="user_inactive")
        return super().validate(attrs)


class EmptyInputSerializer(serializers.Serializer):
    pass


class RefreshOutputSerializer(serializers.Serializer):
    access = serializers.CharField(read_only=True)


class CsrfTokenOutputSerializer(serializers.Serializer):
    csrf_token = serializers.CharField(read_only=True)
