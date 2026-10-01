import uuid

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import serializers, status
from rest_framework.exceptions import APIException, NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsCustomer, IsStaffOrAdmin
from apps.orders.models import Order
from common.serializers import ApiErrorSerializer

from ..models import ExchangeRequest
from ..selectors import (
    get_admin_exchange,
    get_customer_exchange,
    list_admin_exchanges,
    list_customer_exchanges,
)
from ..services import (
    ExchangeConflictError,
    ExchangeError,
    cancel_customer_exchange,
    confirm_replacement_received,
    create_exchange,
    transition_exchange,
)
from .serializers import (
    ExchangeCreateInputSerializer,
    ExchangeOutputSerializer,
    ExchangeTransitionInputSerializer,
)


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "conflict"


class CustomerExchangeListCreateView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(tags=["Exchanges"], responses={200: ExchangeOutputSerializer(many=True)})
    def get(self, request):
        return Response(
            ExchangeOutputSerializer(
                list_customer_exchanges(user_id=request.user.id), many=True
            ).data
        )

    @extend_schema(
        tags=["Exchanges"],
        parameters=[
            OpenApiParameter("Idempotency-Key", uuid.UUID, OpenApiParameter.HEADER, required=True)
        ],
        request=ExchangeCreateInputSerializer,
        responses={201: ExchangeOutputSerializer, 400: ApiErrorSerializer, 409: ApiErrorSerializer},
    )
    def post(self, request):
        serializer = ExchangeCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            key = uuid.UUID(request.headers.get("Idempotency-Key", ""))
        except ValueError as exc:
            raise serializers.ValidationError(
                {"Idempotency-Key": "Header Idempotency-Key phải là UUID hợp lệ."}
            ) from exc
        try:
            exchange, created = create_exchange(
                user=request.user, idempotency_key=key, **serializer.validated_data
            )
        except Order.DoesNotExist as exc:
            raise NotFound("Đơn hàng không tồn tại.") from exc
        except ExchangeError as exc:
            raise Conflict(str(exc)) from exc
        exchange = get_customer_exchange(user_id=request.user.id, exchange_id=exchange.id)
        return Response(
            ExchangeOutputSerializer(exchange).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class CustomerExchangeDetailView(APIView):
    permission_classes = [IsCustomer]

    def _get(self, request, exchange_id: int) -> ExchangeRequest:
        try:
            return get_customer_exchange(user_id=request.user.id, exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist as exc:
            raise NotFound("Yêu cầu đổi hàng không tồn tại.") from exc

    @extend_schema(tags=["Exchanges"], responses={200: ExchangeOutputSerializer})
    def get(self, request, exchange_id: int):
        return Response(ExchangeOutputSerializer(self._get(request, exchange_id)).data)


class CustomerExchangeCancelView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(tags=["Exchanges"], request=None, responses={200: ExchangeOutputSerializer})
    def post(self, request, exchange_id: int):
        try:
            exchange = cancel_customer_exchange(user=request.user, exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist as exc:
            raise NotFound("Yêu cầu đổi hàng không tồn tại.") from exc
        except ExchangeConflictError as exc:
            raise Conflict(str(exc)) from exc
        return Response(
            ExchangeOutputSerializer(
                get_customer_exchange(user_id=request.user.id, exchange_id=exchange.id)
            ).data
        )


class CustomerExchangeConfirmReceivedView(APIView):
    permission_classes = [IsCustomer]

    @extend_schema(tags=["Exchanges"], request=None, responses={200: ExchangeOutputSerializer})
    def post(self, request, exchange_id: int):
        try:
            exchange = confirm_replacement_received(user=request.user, exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist as exc:
            raise NotFound("Yêu cầu đổi hàng không tồn tại.") from exc
        except ExchangeConflictError as exc:
            raise Conflict(str(exc)) from exc
        return Response(
            ExchangeOutputSerializer(
                get_customer_exchange(user_id=request.user.id, exchange_id=exchange.id)
            ).data
        )


class AdminExchangeListView(APIView):
    permission_classes = [IsStaffOrAdmin]

    @extend_schema(tags=["Admin exchanges"], responses={200: ExchangeOutputSerializer(many=True)})
    def get(self, request):
        queryset = list_admin_exchanges(status=request.query_params.get("status", ""))
        return Response(ExchangeOutputSerializer(queryset, many=True).data)


class AdminExchangeDetailView(APIView):
    permission_classes = [IsStaffOrAdmin]

    @extend_schema(tags=["Admin exchanges"], responses={200: ExchangeOutputSerializer})
    def get(self, request, exchange_id: int):
        try:
            exchange = get_admin_exchange(exchange_id=exchange_id)
        except ExchangeRequest.DoesNotExist as exc:
            raise NotFound("Yêu cầu đổi hàng không tồn tại.") from exc
        return Response(ExchangeOutputSerializer(exchange).data)


class AdminExchangeTransitionView(APIView):
    permission_classes = [IsStaffOrAdmin]

    @extend_schema(
        tags=["Admin exchanges"],
        request=ExchangeTransitionInputSerializer,
        responses={200: ExchangeOutputSerializer, 400: ApiErrorSerializer, 409: ApiErrorSerializer},
    )
    def post(self, request, exchange_id: int):
        serializer = ExchangeTransitionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = dict(serializer.validated_data)
        action = data.pop("action")
        received_items = data.pop("received_items", [])
        inspected_items = data.pop("inspected_items", [])
        item_updates = received_items if action == "receive" else inspected_items
        try:
            transition_exchange(
                exchange_id=exchange_id,
                actor=request.user,
                action=action,
                item_updates=item_updates,
                **data,
            )
        except ExchangeRequest.DoesNotExist as exc:
            raise NotFound("Yêu cầu đổi hàng không tồn tại.") from exc
        except (ExchangeError, ExchangeConflictError) as exc:
            raise Conflict(str(exc)) from exc
        return Response(ExchangeOutputSerializer(get_admin_exchange(exchange_id=exchange_id)).data)
