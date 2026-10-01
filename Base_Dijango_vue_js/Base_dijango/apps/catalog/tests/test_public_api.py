import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APIClient

from apps.catalog.models import Product

from .factories import ProductFactory, ProductVariantFactory

pytestmark = pytest.mark.django_db


def test_public_catalog_hides_unpublished_and_filters_available_products():
    available = ProductVariantFactory(inventory=4, price=1_200_000)
    ProductVariantFactory(inventory=0, price=2_000_000)
    ProductFactory(status=Product.Status.DRAFT)
    client = APIClient()

    response = client.get(
        "/api/v1/products/",
        {
            "brand": available.product.brand.slug,
            "size": available.size.label,
            "in_stock": "true",
            "ordering": "price",
        },
    )

    assert response.status_code == 200
    assert response.data["count"] == 1
    product = response.data["results"][0]
    assert product["slug"] == available.product.slug
    assert product["min_price"] == "1200000"
    assert product["is_available"] is True


def test_public_product_detail_hides_draft_product():
    product = ProductFactory(status=Product.Status.DRAFT)

    response = APIClient().get(f"/api/v1/products/{product.slug}/")

    assert response.status_code == 404


def test_public_product_list_does_not_filter_stock_when_parameter_is_omitted():
    available = ProductVariantFactory(inventory=4)

    response = APIClient().get("/api/v1/products/")

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["results"][0]["slug"] == available.product.slug


def test_product_list_query_count_does_not_grow_per_product():
    ProductVariantFactory.create_batch(4, inventory=2)
    client = APIClient()

    with CaptureQueriesContext(connection) as queries:
        response = client.get("/api/v1/products/")

    assert response.status_code == 200
    assert len(queries) <= 8
