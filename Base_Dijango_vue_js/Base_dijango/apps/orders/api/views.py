import uuid

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, serializers, status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import Address
from apps.accounts.permissions import IsCustomer
from apps.engagement.services import VoucherValidationError
from apps.orders.models import CartItem, Order, PaymentAttempt
from apps.orders.payments import (
    PaymentConfigurationError,
    PaymentCreationError,
    create_vnpay_attempt,
    process_vnpay_ipn,
)
from apps.orders.selectors import get_user_cart, get_user_order, list_user_orders
from apps.orders.services import (
    CartItemUnavailableError,
    CartOwnershipError,
    IdempotencyConflictError,
    InsufficientStockError,
    OrderCancellationError,
    OrderReceiptConfirmationError,
    add_cart_item,
    build_checkout_quote,
    cancel_customer_order,
    confirm_customer_received,
    create_order,
    delete_cart_item,
    ensure_user_cart,
    update_cart_item,
)
from common.serializers import ApiErrorSerializer

from .serializers import (
    AddCartItemInputSerializer,
    CartItemOutputSerializer,
    CartOutputSerializer,
    CheckoutInputSerializer,
    CheckoutQuoteOutputSerializer,
    CreateOrderInputSerializer,
    CreatePaymentInputSerializer,
    OrderOutputSerializer,
    PaginatedOrderOutputSerializer,
    PaymentAttemptOutputSerializer,
    PaymentOutputSerializer,
    UpdateCartItemInputSerializer,
    VnpayIpnOutputSerializer,
    VnpayReturnInputSerializer,
    VnpayReturnOutputSerializer,
)


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Dữ liệu xung đột với trạng thái hiện tại."
    default_code = "conflict"


def _get_user_order_or_404(*, user_id: int, order_id: int) -> Order:
    try:
        return get_user_order(user_id=user_id, order_id=order_id)
    except Order.DoesNotExist as exc:
        raise NotFound("Đơn hàng không tồn tại.") from exc


def _raise_cart_error(exc: Exception) -> None:
    if isinstance(exc, CartOwnershipError):
        raise NotFound("Cart item không tồn tại.") from exc
    if isinstance(exc, (CartItemUnavailableError, InsufficientStockError)):
        raise serializers.ValidationError({"cart": str(exc)}) from exc
    raise exc


class CartView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Cart"],
        responses={200: CartOutputSerializer, 401: ApiErrorSerializer, 403: ApiErrorSerializer},
    )
    def get(self, request):
        ensure_user_cart(user=request.user)
        cart = get_user_cart(user_id=request.user.id)
        return Response(CartOutputSerializer(cart, context={"request": request}).data)


class CartItemCreateView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Cart"],
        request=AddCartItemInputSerializer,
        responses={
            201: CartItemOutputSerializer,
            400: ApiErrorSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
        },
    )
    def post(self, request):
        serializer = AddCartItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            item = add_cart_item(user=request.user, **serializer.validated_data)
        except (CartItemUnavailableError, InsufficientStockError) as exc:
            _raise_cart_error(exc)
        item = (
            CartItem.objects.select_related(
                "variant__product__brand",
                "variant__product__category",
                "variant__size",
                "variant__color",
                "variant__inventory",
            )
            .prefetch_related("variant__product__images")
            .get(pk=item.pk)
        )
        return Response(
            CartItemOutputSerializer(item, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class CartItemDetailView(APIView):
    permission_classes = [IsCustomer]

    def _get_item(self, request, item_id: int) -> CartItem:
        return get_object_or_404(CartItem, pk=item_id, cart__user=request.user)

    @extend_schema(
        tags=["Cart"],
        request=UpdateCartItemInputSerializer,
        responses={
            200: CartItemOutputSerializer,
            400: ApiErrorSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            404: ApiErrorSerializer,
        },
    )
    def patch(self, request, item_id: int):
        serializer = UpdateCartItemInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            item = update_cart_item(
                user=request.user,
                item=self._get_item(request, item_id),
                **serializer.validated_data,
            )
        except (CartItemUnavailableError, InsufficientStockError) as exc:
            _raise_cart_error(exc)
        return Response(CartItemOutputSerializer(item, context={"request": request}).data)

    @extend_schema(
        tags=["Cart"],
        responses={
            204: None,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            404: ApiErrorSerializer,
        },
    )
    def delete(self, request, item_id: int):
        item = self._get_item(request, item_id)
        delete_cart_item(user=request.user, item=item)
        return Response(status=status.HTTP_204_NO_CONTENT)


class CheckoutQuoteView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Checkout"],
        request=CheckoutInputSerializer,
        responses={
            200: CheckoutQuoteOutputSerializer,
            400: ApiErrorSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            404: ApiErrorSerializer,
        },
    )
    def post(self, request):
        serializer = CheckoutInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            quote = build_checkout_quote(user=request.user, **serializer.validated_data)
        except Address.DoesNotExist as exc:
            raise NotFound("Địa chỉ không tồn tại.") from exc
        except (
            CartOwnershipError,
            CartItemUnavailableError,
            InsufficientStockError,
            VoucherValidationError,
        ) as exc:
            _raise_cart_error(exc)
        return Response(CheckoutQuoteOutputSerializer(quote).data)


class OrderListCreateView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        operation_id="order_list",
        tags=["Orders"],
        responses={
            200: PaginatedOrderOutputSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
        },
    )
    def get(self, request):
        orders = list_user_orders(user_id=request.user.id)
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(orders, request, view=self)
        serializer = OrderOutputSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(
        operation_id="order_create",
        tags=["Orders"],
        parameters=[
            OpenApiParameter(
                name="Idempotency-Key",
                type=uuid.UUID,
                location=OpenApiParameter.HEADER,
                required=True,
                description=(
                    "UUID ổn định cho mỗi lần submit order; retry phải dùng lại cùng giá trị."
                ),
            )
        ],
        request=CreateOrderInputSerializer,
        responses={
            200: OrderOutputSerializer,
            201: OrderOutputSerializer,
            400: ApiErrorSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            404: ApiErrorSerializer,
            409: ApiErrorSerializer,
        },
    )
    def post(self, request):
        serializer = CreateOrderInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            idempotency_key = uuid.UUID(request.headers.get("Idempotency-Key", ""))
        except ValueError as exc:
            raise serializers.ValidationError(
                {"Idempotency-Key": "Header Idempotency-Key phải là UUID hợp lệ."}
            ) from exc
        try:
            order, created = create_order(
                user=request.user,
                idempotency_key=idempotency_key,
                **serializer.validated_data,
            )
        except Address.DoesNotExist as exc:
            raise NotFound("Địa chỉ không tồn tại.") from exc
        except IdempotencyConflictError as exc:
            raise Conflict(str(exc)) from exc
        except (
            CartOwnershipError,
            CartItemUnavailableError,
            InsufficientStockError,
            VoucherValidationError,
        ) as exc:
            _raise_cart_error(exc)
        order = get_user_order(user_id=request.user.id, order_id=order.id)
        return Response(
            OrderOutputSerializer(order).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class OrderDetailView(APIView):
    permission_classes = [IsCustomer]

    def _get_order(self, request, order_id: int) -> Order:
        return _get_user_order_or_404(user_id=request.user.id, order_id=order_id)

    @extend_schema(
        operation_id="order_retrieve",
        tags=["Orders"],
        responses={
            200: OrderOutputSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            404: ApiErrorSerializer,
        },
    )
    def get(self, request, order_id: int):
        return Response(OrderOutputSerializer(self._get_order(request, order_id)).data)


class OrderCancelView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Orders"],
        request=None,
        responses={
            200: OrderOutputSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            404: ApiErrorSerializer,
            409: ApiErrorSerializer,
        },
    )
    def post(self, request, order_id: int):
        try:
            order = cancel_customer_order(
                user=request.user,
                order=_get_user_order_or_404(user_id=request.user.id, order_id=order_id),
            )
        except OrderCancellationError as exc:
            raise Conflict(str(exc)) from exc
        return Response(
            OrderOutputSerializer(get_user_order(user_id=request.user.id, order_id=order.id)).data
        )


class OrderConfirmReceivedView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        tags=["Orders"],
        request=None,
        responses={200: OrderOutputSerializer, 404: ApiErrorSerializer, 409: ApiErrorSerializer},
    )
    def post(self, request, order_id: int):
        try:
            order = confirm_customer_received(user=request.user, order_id=order_id)
        except Order.DoesNotExist as exc:
            raise NotFound("Đơn hàng không tồn tại.") from exc
        except OrderReceiptConfirmationError as exc:
            raise Conflict(str(exc)) from exc
        return Response(
            OrderOutputSerializer(get_user_order(user_id=request.user.id, order_id=order.id)).data
        )


class OrderPaymentView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        operation_id="order_payment_retrieve",
        tags=["Payments"],
        responses={
            200: PaymentOutputSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            404: ApiErrorSerializer,
        },
    )
    def get(self, request, order_id: int):
        order = _get_user_order_or_404(user_id=request.user.id, order_id=order_id)
        if not hasattr(order, "payment"):
            raise NotFound("Đơn hàng không có thanh toán online.")
        return Response(PaymentOutputSerializer(order.payment).data)

    @extend_schema(
        operation_id="order_payment_create",
        tags=["Payments"],
        parameters=[
            OpenApiParameter(
                name="Idempotency-Key",
                type=uuid.UUID,
                location=OpenApiParameter.HEADER,
                required=True,
                description="UUID ổn định cho lần tạo VNPay checkout.",
            )
        ],
        request=CreatePaymentInputSerializer,
        responses={
            200: PaymentAttemptOutputSerializer,
            201: PaymentAttemptOutputSerializer,
            400: ApiErrorSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            404: ApiErrorSerializer,
            409: ApiErrorSerializer,
        },
    )
    def post(self, request, order_id: int):
        serializer = CreatePaymentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            idempotency_key = uuid.UUID(request.headers.get("Idempotency-Key", ""))
        except ValueError as exc:
            raise serializers.ValidationError(
                {"Idempotency-Key": "Header Idempotency-Key phải là UUID hợp lệ."}
            ) from exc
        try:
            attempt, created = create_vnpay_attempt(
                user=request.user,
                order_id=order_id,
                idempotency_key=idempotency_key,
                ip_address=request.META.get("REMOTE_ADDR", "127.0.0.1"),
                **serializer.validated_data,
            )
        except Order.DoesNotExist as exc:
            raise NotFound("Đơn hàng không tồn tại.") from exc
        except (PaymentConfigurationError, PaymentCreationError) as exc:
            raise Conflict(str(exc)) from exc
        return Response(
            PaymentAttemptOutputSerializer(attempt).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class VnpayReturnView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(
        operation_id="vnpay_return_verify",
        tags=["Payments"],
        request=VnpayReturnInputSerializer,
        responses={200: VnpayReturnOutputSerializer, 404: ApiErrorSerializer},
    )
    def post(self, request, order_id: int):
        serializer = VnpayReturnInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        params = dict(serializer.validated_data["params"])
        reference = params.get("vnp_TxnRef", "")
        if not PaymentAttempt.objects.filter(
            reference=reference,
            payment__order_id=order_id,
            payment__order__user=request.user,
        ).exists():
            raise NotFound("Giao dịch VNPay không thuộc đơn hàng này.")

        result = process_vnpay_ipn(params=params)
        order = _get_user_order_or_404(user_id=request.user.id, order_id=order_id)
        return Response(
            {
                "response_code": result.response_code,
                "message": result.message,
                "order_status": order.status,
                "payment_status": order.payment_status,
            }
        )


class VnpayIpnView(APIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    @extend_schema(
        operation_id="vnpay_ipn",
        tags=["Payments"],
        auth=[],
        responses={200: VnpayIpnOutputSerializer},
    )
    def get(self, request):
        result = process_vnpay_ipn(params=request.query_params.dict())
        return Response({"RspCode": result.response_code, "Message": result.message})
