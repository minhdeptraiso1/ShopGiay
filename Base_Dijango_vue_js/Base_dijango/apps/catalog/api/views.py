from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.catalog.recommendations import (
    personalized_recommendations,
    popular_recommendations,
    similar_recommendations,
)
from apps.catalog.selectors import (
    get_public_product,
    list_public_brands,
    list_public_categories,
    list_public_colors,
    list_public_products,
    list_public_sizes,
)
from apps.catalog.services import record_product_event
from common.serializers import ApiErrorSerializer

from .serializers import (
    BrandSerializer,
    CategorySerializer,
    ColorSerializer,
    ProductDetailSerializer,
    ProductEventInputSerializer,
    ProductEventOutputSerializer,
    ProductFilterSerializer,
    ProductListSerializer,
    RecommendationQuerySerializer,
    RecommendationResponseSerializer,
    SizeFilterSerializer,
    SizeSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["Catalog"], responses={200: CategorySerializer(many=True)})
)
class PublicCategoryViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = CategorySerializer
    pagination_class = None

    def get_queryset(self):
        return list_public_categories()


@extend_schema_view(
    list=extend_schema(tags=["Catalog"], responses={200: BrandSerializer(many=True)})
)
class PublicBrandViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = BrandSerializer
    pagination_class = None

    def get_queryset(self):
        return list_public_brands()


@extend_schema_view(list=extend_schema(tags=["Catalog"], parameters=[SizeFilterSerializer]))
class PublicSizeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = SizeSerializer
    pagination_class = None

    def get_queryset(self):
        filters = SizeFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        return list_public_sizes(**filters.validated_data)


@extend_schema_view(
    list=extend_schema(tags=["Catalog"], responses={200: ColorSerializer(many=True)})
)
class PublicColorViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = ColorSerializer
    pagination_class = None

    def get_queryset(self):
        return list_public_colors()


class PublicProductViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    lookup_field = "slug"

    def get_serializer_class(self):
        return ProductDetailSerializer if self.action == "retrieve" else ProductListSerializer

    def get_queryset(self):
        if self.action == "retrieve":
            return list_public_products()
        filters = ProductFilterSerializer(data=self.request.query_params)
        filters.is_valid(raise_exception=True)
        return list_public_products(**filters.validated_data)

    def get_object(self):
        if self.action == "retrieve":
            return get_public_product(slug=self.kwargs["slug"])
        return super().get_object()

    @extend_schema(
        tags=["Catalog"],
        parameters=[ProductFilterSerializer],
        responses={200: ProductListSerializer(many=True), 400: ApiErrorSerializer},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=["Catalog"],
        responses={200: ProductDetailSerializer, 404: ApiErrorSerializer},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class EventThrottle(ScopedRateThrottle):
    scope = "event"


class ProductEventView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [EventThrottle]

    @extend_schema(
        tags=["Events"],
        request=ProductEventInputSerializer,
        responses={
            200: ProductEventOutputSerializer,
            201: ProductEventOutputSerializer,
            400: ApiErrorSerializer,
            429: ApiErrorSerializer,
        },
    )
    def post(self, request):
        serializer = ProductEventInputSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = request.user if request.user.is_authenticated else None
        event, created = record_product_event(data=serializer.validated_data, user=user)
        return Response(
            ProductEventOutputSerializer(event).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class RecommendationView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [EventThrottle]
    strategy = "popular"

    @extend_schema(
        tags=["Recommendations"],
        parameters=[RecommendationQuerySerializer],
        responses={200: RecommendationResponseSerializer},
    )
    def get(self, request, product_id: int | None = None):
        query = RecommendationQuerySerializer(data=request.query_params)
        query.is_valid(raise_exception=True)
        user = request.user if request.user.is_authenticated else None
        anonymous_id = query.validated_data.get("anonymous_id")
        limit = query.validated_data["limit"]
        if self.strategy == "personalized":
            result = personalized_recommendations(user=user, anonymous_id=anonymous_id, limit=limit)
        elif self.strategy == "similar":
            source = get_object_or_404(list_public_products(), pk=product_id)
            result = similar_recommendations(
                source=source, user=user, anonymous_id=anonymous_id, limit=limit
            )
        else:
            result = popular_recommendations(user=user, anonymous_id=anonymous_id, limit=limit)
        payload = {
            "request_id": result.request.id,
            "strategy": result.request.strategy,
            "fallback_used": result.fallback_used,
            "results": result.products,
        }
        return Response(
            RecommendationResponseSerializer(payload, context={"request": request}).data
        )


class PopularRecommendationView(RecommendationView):
    strategy = "popular"


class PersonalizedRecommendationView(RecommendationView):
    strategy = "personalized"


class SimilarRecommendationView(RecommendationView):
    strategy = "similar"
