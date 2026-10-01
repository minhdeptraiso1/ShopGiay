from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.selectors import get_user_address, list_user_addresses
from apps.accounts.services import (
    create_address,
    delete_address,
    set_default_address,
    update_address,
)
from common.serializers import ApiErrorSerializer

from .serializers import AddressInputSerializer, AddressOutputSerializer


def _get_owned_address(*, user, address_id: int):
    address = get_user_address(user=user, address_id=address_id)
    if address is None:
        raise NotFound("Không tìm thấy địa chỉ.", code="address_not_found")
    return address


class AddressListCreateView(APIView):
    @extend_schema(tags=["Addresses"], responses={200: AddressOutputSerializer(many=True)})
    def get(self, request):
        addresses = list_user_addresses(user=request.user)
        return Response(AddressOutputSerializer(addresses, many=True).data)

    @extend_schema(
        tags=["Addresses"],
        request=AddressInputSerializer,
        responses={201: AddressOutputSerializer, 400: ApiErrorSerializer},
    )
    def post(self, request):
        serializer = AddressInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        address = create_address(user=request.user, **serializer.validated_data)
        return Response(AddressOutputSerializer(address).data, status=status.HTTP_201_CREATED)


class AddressDetailView(APIView):
    @extend_schema(
        tags=["Addresses"],
        responses={200: AddressOutputSerializer, 404: ApiErrorSerializer},
    )
    def get(self, request, address_id: int):
        address = _get_owned_address(user=request.user, address_id=address_id)
        return Response(AddressOutputSerializer(address).data)

    @extend_schema(
        tags=["Addresses"],
        request=AddressInputSerializer,
        responses={200: AddressOutputSerializer, 400: ApiErrorSerializer, 404: ApiErrorSerializer},
    )
    def patch(self, request, address_id: int):
        address = _get_owned_address(user=request.user, address_id=address_id)
        serializer = AddressInputSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated = update_address(address=address, **serializer.validated_data)
        return Response(AddressOutputSerializer(updated).data)

    @extend_schema(
        tags=["Addresses"],
        responses={
            204: OpenApiResponse(description="Địa chỉ đã được xóa"),
            404: ApiErrorSerializer,
        },
    )
    def delete(self, request, address_id: int):
        address = _get_owned_address(user=request.user, address_id=address_id)
        delete_address(address=address)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetDefaultAddressView(APIView):
    @extend_schema(
        tags=["Addresses"],
        request=None,
        responses={200: AddressOutputSerializer, 404: ApiErrorSerializer},
    )
    def post(self, request, address_id: int):
        address = _get_owned_address(user=request.user, address_id=address_id)
        return Response(AddressOutputSerializer(set_default_address(address=address)).data)
