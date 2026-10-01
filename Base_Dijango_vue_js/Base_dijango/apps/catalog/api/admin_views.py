from collections.abc import Callable
from datetime import timedelta
from decimal import Decimal
from typing import Any

from django.db.models import Count
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import serializers, status, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsAdmin, IsStaffOrAdmin
from apps.catalog.models import (
    Brand,
    Category,
    Color,
    Product,
    ProductEvent,
    ProductImage,
    ProductVariant,
    RecommendationItem,
    RecommendationRequest,
    Size,
    StockMovement,
)
from apps.catalog.services import (
    InsufficientStockError,
    adjust_inventory,
    create_brand,
    create_category,
    create_color,
    create_product,
    create_product_image,
    create_size,
    create_variant,
    deactivate_brand,
    deactivate_category,
    deactivate_color,
    deactivate_product,
    deactivate_size,
    deactivate_variant,
    delete_product_image,
    update_brand,
    update_category,
    update_color,
    update_product,
    update_product_image,
    update_size,
    update_variant,
)
from common.serializers import ApiErrorSerializer

from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ColorSerializer,
    InventoryAdjustmentInputSerializer,
    ProductAdminSerializer,
    ProductImageSerializer,
    ProductVariantAdminSerializer,
    RecommendationMetricsSerializer,
    SizeSerializer,
    StockMovementSerializer,
)

WriteService = Callable[..., Any]


class RecommendationMetricsView(APIView):
    permission_classes = [IsStaffOrAdmin]

    @extend_schema(tags=["Recommendations"], responses={200: RecommendationMetricsSerializer})
    def get(self, request):
        since = timezone.now() - timedelta(days=30)
        requests = RecommendationRequest.objects.filter(created_at__gte=since)
        events = ProductEvent.objects.filter(
            created_at__gte=since, recommendation_context_id__isnull=False
        )
        impressions = events.filter(
            event_type=ProductEvent.EventType.RECOMMENDATION_IMPRESSION
        ).count()
        clicks = events.filter(event_type=ProductEvent.EventType.RECOMMENDATION_CLICK).count()
        recommended_products = (
            RecommendationItem.objects.filter(request__created_at__gte=since)
            .values("product_id")
            .distinct()
            .count()
        )
        active_products = Product.objects.filter(status=Product.Status.PUBLISHED).count()
        by_strategy = {
            row["strategy"]: row["count"]
            for row in requests.values("strategy").annotate(count=Count("id"))
        }
        payload = {
            "days": 30,
            "requests": requests.count(),
            "impressions": impressions,
            "clicks": clicks,
            "attributed_add_to_carts": events.filter(
                event_type=ProductEvent.EventType.ADD_CART
            ).count(),
            "attributed_purchases": events.filter(
                event_type=ProductEvent.EventType.PURCHASE
            ).count(),
            "ctr_percent": (
                Decimal(clicks * 100) / Decimal(impressions) if impressions else Decimal("0")
            ),
            "coverage_percent": (
                Decimal(recommended_products * 100) / Decimal(active_products)
                if active_products
                else Decimal("0")
            ),
            "requests_by_strategy": by_strategy,
        }
        return Response(RecommendationMetricsSerializer(payload).data)


def _catalog_admin_schema(serializer_class):
    common_errors = {401: ApiErrorSerializer, 403: ApiErrorSerializer, 404: ApiErrorSerializer}
    write_errors = {400: ApiErrorSerializer, **common_errors}
    return extend_schema_view(
        list=extend_schema(
            tags=["Catalog administration"],
            responses={200: serializer_class(many=True), **common_errors},
        ),
        retrieve=extend_schema(
            tags=["Catalog administration"], responses={200: serializer_class, **common_errors}
        ),
        create=extend_schema(
            tags=["Catalog administration"], responses={201: serializer_class, **write_errors}
        ),
        update=extend_schema(
            tags=["Catalog administration"], responses={200: serializer_class, **write_errors}
        ),
        partial_update=extend_schema(
            tags=["Catalog administration"], responses={200: serializer_class, **write_errors}
        ),
        destroy=extend_schema(
            tags=["Catalog administration"], responses={204: None, **common_errors}
        ),
    )


class ServiceModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdmin]
    create_service: WriteService
    update_service: WriteService
    destroy_service: WriteService
    service_argument: str

    def perform_create(self, serializer):
        self.created_instance = self.create_service(data=serializer.validated_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        output = self.get_serializer(self.created_instance)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        kwargs = {
            self.service_argument: serializer.instance,
            "data": serializer.validated_data,
        }
        self.updated_instance = self.update_service(**kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(self.get_serializer(self.updated_instance).data)

    def perform_destroy(self, instance):
        self.destroy_service(**{self.service_argument: instance})


@_catalog_admin_schema(CategorySerializer)
class CategoryAdminViewSet(ServiceModelViewSet):
    queryset = Category.objects.select_related("parent").all()
    serializer_class = CategorySerializer
    create_service = staticmethod(create_category)
    update_service = staticmethod(update_category)
    destroy_service = staticmethod(deactivate_category)
    service_argument = "category"


@_catalog_admin_schema(BrandSerializer)
class BrandAdminViewSet(ServiceModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    create_service = staticmethod(create_brand)
    update_service = staticmethod(update_brand)
    destroy_service = staticmethod(deactivate_brand)
    service_argument = "brand"


@_catalog_admin_schema(ProductAdminSerializer)
class ProductAdminViewSet(ServiceModelViewSet):
    queryset = Product.objects.select_related("category", "brand").all()
    serializer_class = ProductAdminSerializer
    create_service = staticmethod(create_product)
    update_service = staticmethod(update_product)
    destroy_service = staticmethod(deactivate_product)
    service_argument = "product"


@_catalog_admin_schema(SizeSerializer)
class SizeAdminViewSet(ServiceModelViewSet):
    queryset = Size.objects.select_related("brand").all()
    serializer_class = SizeSerializer
    create_service = staticmethod(create_size)
    update_service = staticmethod(update_size)
    destroy_service = staticmethod(deactivate_size)
    service_argument = "size"


@_catalog_admin_schema(ColorSerializer)
class ColorAdminViewSet(ServiceModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    create_service = staticmethod(create_color)
    update_service = staticmethod(update_color)
    destroy_service = staticmethod(deactivate_color)
    service_argument = "color"


@_catalog_admin_schema(ProductVariantAdminSerializer)
class ProductVariantAdminViewSet(ServiceModelViewSet):
    queryset = ProductVariant.objects.select_related("product", "size", "color", "inventory").all()
    serializer_class = ProductVariantAdminSerializer
    create_service = staticmethod(create_variant)
    update_service = staticmethod(update_variant)
    destroy_service = staticmethod(deactivate_variant)
    service_argument = "variant"

    def get_permissions(self):
        permission_classes = [IsStaffOrAdmin] if self.action in {"list", "retrieve"} else [IsAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get("product")
        return queryset.filter(product_id=product_id) if product_id else queryset


@_catalog_admin_schema(ProductImageSerializer)
class ProductImageAdminViewSet(ServiceModelViewSet):
    queryset = ProductImage.objects.select_related("product").all()
    serializer_class = ProductImageSerializer
    parser_classes = [MultiPartParser, FormParser]
    create_service = staticmethod(create_product_image)
    update_service = staticmethod(update_product_image)
    destroy_service = staticmethod(delete_product_image)
    service_argument = "image"

    def get_queryset(self):
        queryset = super().get_queryset()
        product_id = self.request.query_params.get("product")
        return queryset.filter(product_id=product_id) if product_id else queryset


class InventoryAdjustmentView(APIView):
    permission_classes = [IsStaffOrAdmin]

    @extend_schema(
        tags=["Inventory"],
        request=InventoryAdjustmentInputSerializer,
        responses={
            201: StockMovementSerializer,
            400: ApiErrorSerializer,
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
            404: ApiErrorSerializer,
        },
    )
    def post(self, request, variant_id: int):
        serializer = InventoryAdjustmentInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            movement = adjust_inventory(
                variant_id=variant_id,
                actor=request.user,
                **serializer.validated_data,
            )
        except ProductVariant.DoesNotExist:
            raise NotFound("Variant không tồn tại.") from None
        except InsufficientStockError as exc:
            raise serializers.ValidationError({"delta": str(exc)}) from exc
        return Response(StockMovementSerializer(movement).data, status=status.HTTP_201_CREATED)


class StockMovementListView(ListAPIView):
    permission_classes = [IsStaffOrAdmin]
    serializer_class = StockMovementSerializer

    def get_queryset(self):
        return StockMovement.objects.filter(variant_id=self.kwargs["variant_id"]).select_related(
            "actor"
        )

    @extend_schema(
        tags=["Inventory"],
        responses={
            200: StockMovementSerializer(many=True),
            401: ApiErrorSerializer,
            403: ApiErrorSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
