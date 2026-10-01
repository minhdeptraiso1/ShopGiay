from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from apps.accounts.models import Address
from apps.accounts.roles import get_business_roles

User = get_user_model()


class UserOutputSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    loyalty_points = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "is_active",
            "date_joined",
            "roles",
            "permissions",
            "loyalty_points",
        )
        read_only_fields = fields

    def get_roles(self, user) -> list[str]:
        return get_business_roles(user)

    def get_permissions(self, user) -> list[str]:
        return sorted(user.get_all_permissions())

    def get_loyalty_points(self, user) -> int:
        account = getattr(user, "loyalty_account", None)
        return account.balance if account else 0


class RegisterInputSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    full_name = serializers.CharField(max_length=255, trim_whitespace=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_email(self, value: str) -> str:
        normalized_email = User.objects.normalize_email_address(value)
        if User.objects.filter(email=normalized_email).exists():
            raise serializers.ValidationError("Email này đã được sử dụng.", code="unique")
        return normalized_email

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Mật khẩu xác nhận không khớp."}, code="password_mismatch"
            )
        candidate = User(email=attrs["email"], full_name=attrs["full_name"])
        validate_password(attrs["password"], user=candidate)
        return attrs


class RegisterOutputSerializer(serializers.Serializer):
    user = UserOutputSerializer(read_only=True)


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


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField(max_length=128)
    token = serializers.CharField(max_length=256)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password_confirm = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Mật khẩu xác nhận không khớp."},
                code="password_mismatch",
            )
        validate_password(attrs["new_password"])
        return attrs


class MessageOutputSerializer(serializers.Serializer):
    message = serializers.CharField(read_only=True)


class AddressOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            "id",
            "recipient_name",
            "phone_number",
            "province",
            "district",
            "ward",
            "street_address",
            "is_default",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class AddressInputSerializer(serializers.Serializer):
    recipient_name = serializers.CharField(max_length=255, trim_whitespace=True)
    phone_number = serializers.RegexField(
        regex=r"^\+?[0-9][0-9 .-]{7,18}[0-9]$",
        max_length=20,
        error_messages={"invalid": "Số điện thoại chưa đúng định dạng."},
    )
    province = serializers.CharField(max_length=100, trim_whitespace=True)
    district = serializers.CharField(max_length=100, trim_whitespace=True)
    ward = serializers.CharField(max_length=100, trim_whitespace=True)
    street_address = serializers.CharField(max_length=255, trim_whitespace=True)
