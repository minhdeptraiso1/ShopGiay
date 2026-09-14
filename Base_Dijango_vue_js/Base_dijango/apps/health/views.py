import logging

from django.core.cache import cache
from django.db import connections
from django.db.utils import DatabaseError
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class LivenessSerializer(serializers.Serializer):
    status = serializers.CharField(read_only=True)


class ReadinessChecksSerializer(serializers.Serializer):
    database = serializers.BooleanField(read_only=True)
    redis = serializers.BooleanField(read_only=True)


class ReadinessSerializer(serializers.Serializer):
    status = serializers.CharField(read_only=True)
    checks = ReadinessChecksSerializer(read_only=True)


class LivenessView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=["Health"], responses={200: LivenessSerializer})
    def get(self, request):
        return Response({"status": "ok"})


class ReadinessView(APIView):
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @extend_schema(tags=["Health"], responses={200: ReadinessSerializer, 503: ReadinessSerializer})
    def get(self, request):
        checks = {"database": False, "redis": False}
        try:
            with connections["default"].cursor() as cursor:
                cursor.execute("SELECT 1")
            checks["database"] = True
        except DatabaseError:
            logger.warning("Readiness database check failed")

        try:
            cache.set("health:ready", "1", timeout=5)
            checks["redis"] = cache.get("health:ready") == "1"
        except Exception:
            logger.warning("Readiness Redis check failed", exc_info=True)

        is_ready = all(checks.values())
        return Response(
            {"status": "ok" if is_ready else "unavailable", "checks": checks},
            status=status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        )
