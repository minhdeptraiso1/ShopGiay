import uuid

import pytest
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from apps.accounts.roles import BusinessRole
from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import Product, ProductEvent, RecommendationRequest
from apps.catalog.tests.factories import ProductFactory, ProductVariantFactory

pytestmark = pytest.mark.django_db


def make_customer_client():
    user = UserFactory()
    group, _ = Group.objects.get_or_create(name=BusinessRole.CUSTOMER)
    user.groups.add(group)
    client = APIClient()
    client.force_authenticate(user)
    return client, user


def test_popular_and_personalized_recommendations_have_fallback_and_ranked_items():
    first = ProductVariantFactory(inventory=5).product
    second = ProductVariantFactory(inventory=5).product
    client, user = make_customer_client()
    ProductEvent.objects.create(
        client_event_id=uuid.uuid4(),
        event_type=ProductEvent.EventType.VIEW,
        source=ProductEvent.Source.STOREFRONT,
        product=second,
        user=user,
    )

    popular = client.get("/api/v1/recommendations/popular/?limit=2")
    personalized = client.get("/api/v1/recommendations/personalized/?limit=2")

    assert popular.status_code == 200
    assert len(popular.data["results"]) == 2
    assert personalized.status_code == 200
    assert personalized.data["strategy"] == RecommendationRequest.Strategy.PERSONALIZED
    assert personalized.data["results"][0]["id"] == second.id
    assert {first.id, second.id} == {row["id"] for row in popular.data["results"]}


def test_similar_footwear_includes_accessories_and_care_products():
    shoe = ProductVariantFactory(inventory=5).product
    ProductVariantFactory(inventory=5)
    accessory = ProductFactory(product_type=Product.ProductType.ACCESSORY)
    ProductVariantFactory(
        product=accessory,
        size=None,
        color=None,
        option_label="Freesize",
        inventory=8,
    )
    care = ProductFactory(product_type=Product.ProductType.CARE)
    ProductVariantFactory(
        product=care,
        size=None,
        color=None,
        option_label="Chai 250 ml",
        inventory=8,
    )

    response = APIClient().get(
        f"/api/v1/products/{shoe.id}/recommendations/",
        {"anonymous_id": str(uuid.uuid4()), "limit": 4},
    )

    assert response.status_code == 200
    types = {row["product_type"] for row in response.data["results"]}
    assert Product.ProductType.ACCESSORY in types
    assert Product.ProductType.CARE in types


def test_recommendation_click_is_attributed_to_add_cart_and_metrics():
    variant = ProductVariantFactory(inventory=5)
    client, user = make_customer_client()
    recommendation = client.get("/api/v1/recommendations/popular/?limit=1")
    request_id = recommendation.data["request_id"]
    client.post(
        "/api/v1/events/",
        {
            "client_event_id": str(uuid.uuid4()),
            "schema_version": 1,
            "event_type": ProductEvent.EventType.RECOMMENDATION_CLICK,
            "source": ProductEvent.Source.RECOMMENDATION,
            "product": variant.product_id,
            "recommendation_context_id": request_id,
        },
        format="json",
    )
    added = client.post(
        "/api/v1/cart/items/",
        {
            "variant": variant.id,
            "quantity": 1,
            "recommendation_context_id": request_id,
        },
        format="json",
    )
    metrics = client.get("/api/v1/admin/recommendations/metrics/")

    assert added.status_code == 201
    assert ProductEvent.objects.filter(
        user=user,
        event_type=ProductEvent.EventType.ADD_CART,
        recommendation_context_id=request_id,
    ).exists()
    assert metrics.status_code == 403
