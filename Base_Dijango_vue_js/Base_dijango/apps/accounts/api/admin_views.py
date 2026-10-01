from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsStaffOrAdmin
from common.serializers import ApiErrorSerializer

from .serializers import MessageOutputSerializer


class AdminAccessView(APIView):
    permission_classes = [IsStaffOrAdmin]

    @extend_schema(
        tags=["Administration"],
        responses={
            200: MessageOutputSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
        },
    )
    def get(self, request):
        return Response({"message": "Quyền truy cập quản trị hợp lệ."})
