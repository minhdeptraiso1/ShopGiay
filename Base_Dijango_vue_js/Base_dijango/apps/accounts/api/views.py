from django.conf import settings
from django.middleware.csrf import get_token
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from apps.accounts.services import (
    DuplicateEmailError,
    InvalidPasswordResetTokenError,
    confirm_password_reset,
    register_customer,
    request_password_reset,
    update_profile,
)
from common.exceptions import api_exception_handler
from common.serializers import ApiErrorSerializer

from .cookies import delete_refresh_cookie, prevent_sensitive_response_caching, set_refresh_cookie
from .serializers import (
    ActiveUserTokenRefreshSerializer,
    CsrfTokenOutputSerializer,
    EmptyInputSerializer,
    LoginInputSerializer,
    LoginOutputSerializer,
    MessageOutputSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RefreshOutputSerializer,
    RegisterInputSerializer,
    RegisterOutputSerializer,
    UpdateProfileInputSerializer,
    UserOutputSerializer,
)


class LoginThrottle(AnonRateThrottle):
    scope = "login"


class RefreshThrottle(AnonRateThrottle):
    scope = "refresh"


class RegisterThrottle(AnonRateThrottle):
    scope = "register"


class PasswordResetThrottle(AnonRateThrottle):
    scope = "password_reset"


def _dummy_get_response(request):
    return None


class EnforceCSRFMixin:
    def initial(self, request, *args, **kwargs) -> None:
        check = CSRFCheck(_dummy_get_response)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise PermissionDenied(f"CSRF Failed: {reason}", code="csrf_failed")
        super().initial(request, *args, **kwargs)


class CsrfTokenView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(tags=["Authentication"], responses={200: CsrfTokenOutputSerializer})
    def get(self, request):
        response = Response({"csrf_token": get_token(request._request)})
        return prevent_sensitive_response_caching(response)


class LoginView(EnforceCSRFMixin, APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [LoginThrottle]

    def get_authenticate_header(self, request):
        return "Bearer"

    @extend_schema(
        tags=["Authentication"],
        request=LoginInputSerializer,
        responses={
            200: LoginOutputSerializer,
            400: ApiErrorSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            429: ApiErrorSerializer,
        },
    )
    def post(self, request):
        serializer = LoginInputSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        output = {
            "access": str(refresh.access_token),
            "user": UserOutputSerializer(user).data,
        }
        response = Response(output)
        set_refresh_cookie(response, str(refresh))
        return prevent_sensitive_response_caching(response)


class RegisterView(EnforceCSRFMixin, APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [RegisterThrottle]

    @extend_schema(
        tags=["Authentication"],
        request=RegisterInputSerializer,
        responses={
            201: RegisterOutputSerializer,
            400: ApiErrorSerializer,
            403: ApiErrorSerializer,
            429: ApiErrorSerializer,
        },
    )
    def post(self, request):
        serializer = RegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = register_customer(
                email=serializer.validated_data["email"],
                full_name=serializer.validated_data["full_name"],
                password=serializer.validated_data["password"],
            )
        except DuplicateEmailError as exc:
            raise ValidationError({"email": "Email này đã được sử dụng."}, code="unique") from exc
        return Response({"user": UserOutputSerializer(user).data}, status=status.HTTP_201_CREATED)


class PasswordResetRequestView(EnforceCSRFMixin, APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [PasswordResetThrottle]

    @extend_schema(
        tags=["Authentication"],
        request=PasswordResetRequestSerializer,
        responses={
            202: MessageOutputSerializer,
            400: ApiErrorSerializer,
            403: ApiErrorSerializer,
            429: ApiErrorSerializer,
        },
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_password_reset(email=serializer.validated_data["email"])
        return Response(
            {"message": "Nếu email tồn tại, hướng dẫn đặt lại mật khẩu đã được gửi."},
            status=status.HTTP_202_ACCEPTED,
        )


class PasswordResetConfirmView(EnforceCSRFMixin, APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [PasswordResetThrottle]

    @extend_schema(
        tags=["Authentication"],
        request=PasswordResetConfirmSerializer,
        responses={
            204: OpenApiResponse(description="Mật khẩu đã được cập nhật"),
            400: ApiErrorSerializer,
            403: ApiErrorSerializer,
            429: ApiErrorSerializer,
        },
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            confirm_password_reset(
                uid=serializer.validated_data["uid"],
                token=serializer.validated_data["token"],
                new_password=serializer.validated_data["new_password"],
            )
        except InvalidPasswordResetTokenError as exc:
            raise ValidationError(
                {"token": "Liên kết đặt lại mật khẩu không hợp lệ hoặc đã hết hạn."},
                code="invalid_reset_token",
            ) from exc
        return Response(status=status.HTTP_204_NO_CONTENT)


class RefreshView(EnforceCSRFMixin, APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [RefreshThrottle]

    def get_authenticate_header(self, request):
        return "Bearer"

    @extend_schema(
        tags=["Authentication"],
        request=EmptyInputSerializer,
        responses={
            200: RefreshOutputSerializer,
            400: ApiErrorSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            429: ApiErrorSerializer,
        },
    )
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        if not refresh_token:
            raise AuthenticationFailed("Không có phiên đăng nhập.", code="session_missing")

        serializer = ActiveUserTokenRefreshSerializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except APIException as exc:
            response = api_exception_handler(exc, {"request": request, "view": self})
            delete_refresh_cookie(response)
            return prevent_sensitive_response_caching(response)

        rotated_refresh = serializer.validated_data["refresh"]
        response = Response({"access": serializer.validated_data["access"]})
        set_refresh_cookie(response, rotated_refresh)
        return prevent_sensitive_response_caching(response)


class LogoutView(EnforceCSRFMixin, APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=["Authentication"],
        request=EmptyInputSerializer,
        responses={
            204: OpenApiResponse(description="Refresh token đã bị thu hồi"),
            403: ApiErrorSerializer,
        },
    )
    def post(self, request):
        refresh_token = request.COOKIES.get(settings.REFRESH_TOKEN_COOKIE_NAME)
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass
        response = Response(status=status.HTTP_204_NO_CONTENT)
        delete_refresh_cookie(response)
        return prevent_sensitive_response_caching(response)


class MeView(APIView):
    @extend_schema(tags=["Profile"], responses={200: UserOutputSerializer, 401: ApiErrorSerializer})
    def get(self, request):
        return Response(UserOutputSerializer(request.user).data)

    @extend_schema(
        tags=["Profile"],
        request=UpdateProfileInputSerializer,
        responses={
            200: UserOutputSerializer,
            400: ApiErrorSerializer,
            401: ApiErrorSerializer,
        },
    )
    def patch(self, request):
        serializer = UpdateProfileInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = update_profile(user=request.user, **serializer.validated_data)
        return Response(UserOutputSerializer(user).data)
