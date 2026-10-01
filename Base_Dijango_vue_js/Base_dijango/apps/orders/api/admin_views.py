from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsStaffOrAdmin
from apps.orders.fulfillment import OrderTransitionError, StaleOrderError, transition_order
from apps.orders.models import Order
from apps.orders.selectors import get_admin_order, list_admin_orders
from common.serializers import ApiErrorSerializer

from .admin_serializers import (
    AdminOrderOutputSerializer,
    OrderTransitionInputSerializer,
    PaginatedAdminOrderOutputSerializer,
)


class Conflict(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "conflict"


class AdminOrderListView(APIView):
    permission_classes = [IsStaffOrAdmin]

    @extend_schema(
        operation_id="admin_order_list",
        tags=["Admin orders"],
        parameters=[
            OpenApiParameter("status", str, required=False, enum=Order.Status.values),
        ],
        responses={
            200: PaginatedAdminOrderOutputSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
        },
    )
    def get(self, request):
        queryset = list_admin_orders(status=request.query_params.get("status"))
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(AdminOrderOutputSerializer(page, many=True).data)


class AdminOrderDetailView(APIView):
    permission_classes = [IsStaffOrAdmin]

    @extend_schema(
        operation_id="admin_order_retrieve",
        tags=["Admin orders"],
        responses={
            200: AdminOrderOutputSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            404: ApiErrorSerializer,
        },
    )
    def get(self, request, order_id: int):
        order = get_object_or_404(get_admin_order(), pk=order_id)
        return Response(AdminOrderOutputSerializer(order).data)


class AdminOrderTransitionView(APIView):
    permission_classes = [IsStaffOrAdmin]

    @extend_schema(
        operation_id="admin_order_transition",
        tags=["Admin orders"],
        request=OrderTransitionInputSerializer,
        responses={
            200: AdminOrderOutputSerializer,
            400: ApiErrorSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            404: ApiErrorSerializer,
            409: ApiErrorSerializer,
        },
    )
    def post(self, request, order_id: int):
        get_object_or_404(Order, pk=order_id)
        serializer = OrderTransitionInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            transition_order(order_id=order_id, actor=request.user, **serializer.validated_data)
        except (OrderTransitionError, StaleOrderError) as exc:
            raise Conflict(str(exc)) from exc
        order = get_admin_order().get(pk=order_id)
        return Response(AdminOrderOutputSerializer(order).data)
