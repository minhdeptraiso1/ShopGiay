import pytest
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.accounts.roles import BusinessRole
from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import Category, Product, ProductImage

from .factories import (
    BrandFactory,
    CategoryFactory,
    ColorFactory,
    ProductFactory,
    ProductVariantFactory,
    SizeFactory,
)

pytestmark = pytest.mark.django_db


def authenticated_client(role: BusinessRole) -> APIClient:
    user = UserFactory()
    group, _ = Group.objects.get_or_create(name=role)
    user.groups.add(group)
    client = APIClient()
    client.force_authenticate(user)
    return client


def test_customer_cannot_create_catalog_data():
    response = authenticated_client(BusinessRole.CUSTOMER).post(
        "/api/v1/admin/categories/",
        {"name": "Sneaker", "slug": "sneaker"},
        format="json",
    )

    assert response.status_code == 403
    assert not Category.objects.filter(slug="sneaker").exists()


def test_admin_can_create_and_soft_deactivate_product():
    category = CategoryFactory()
    brand = BrandFactory()
    client = authenticated_client(BusinessRole.ADMIN)
    response = client.post(
        "/api/v1/admin/products/",
        {
            "category": category.id,
            "brand": brand.id,
            "name": "Runner Pro",
            "slug": "runner-pro",
            "description": "Giày chạy bộ",
            "status": Product.Status.PUBLISHED,
        },
        format="json",
    )
    assert response.status_code == 201
    product = Product.objects.get(slug="runner-pro")
    assert product.published_at is not None

    delete_response = client.delete(f"/api/v1/admin/products/{product.id}/")

    assert delete_response.status_code == 204
    product.refresh_from_db()
    assert product.status == Product.Status.INACTIVE


def test_staff_cannot_create_products():
    product = ProductFactory()
    response = authenticated_client(BusinessRole.STAFF).patch(
        f"/api/v1/admin/products/{product.id}/",
        {"name": "Tên bị chặn"},
        format="json",
    )

    assert response.status_code == 403


def test_staff_can_read_variants_but_cannot_change_them():
    product = ProductFactory()
    size = SizeFactory(brand=product.brand)
    variant = ProductVariantFactory(product=product, size=size, inventory=6)
    client = authenticated_client(BusinessRole.STAFF)

    list_response = client.get("/api/v1/admin/variants/")
    update_response = client.patch(
        f"/api/v1/admin/variants/{variant.id}/",
        {"price": "2000000"},
        format="json",
    )

    assert list_response.status_code == 200
    assert any(item["id"] == variant.id for item in list_response.data["results"])
    assert update_response.status_code == 403


def test_admin_creates_variant_with_zero_inventory_and_validates_image_type():
    product = ProductFactory()
    size = SizeFactory(brand=product.brand)
    color = ColorFactory()
    client = authenticated_client(BusinessRole.ADMIN)

    variant_response = client.post(
        "/api/v1/admin/variants/",
        {
            "product": product.id,
            "size": size.id,
            "color": color.id,
            "sku": "RUNNER-BLK-42",
            "price": "1800000",
            "currency": "VND",
            "low_stock_threshold": 4,
        },
        format="json",
    )

    assert variant_response.status_code == 201
    assert variant_response.data["inventory_quantity"] == 0

    invalid_image = SimpleUploadedFile("payload.txt", b"not-an-image", content_type="text/plain")
    image_response = client.post(
        "/api/v1/admin/product-images/",
        {"product": product.id, "image": invalid_image, "is_primary": True},
        format="multipart",
    )

    assert image_response.status_code == 400


def test_variant_size_must_belong_to_product_brand():
    product = ProductFactory()
    other_brand_size = SizeFactory()
    color = ColorFactory()

    response = authenticated_client(BusinessRole.ADMIN).post(
        "/api/v1/admin/variants/",
        {
            "product": product.id,
            "size": other_brand_size.id,
            "color": color.id,
            "sku": "INVALID-BRAND-SIZE",
            "price": "1000000",
        },
        format="json",
    )

    assert response.status_code == 400
    assert "size" in response.data["details"]


def test_new_primary_image_replaces_previous_primary(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    product = ProductFactory()
    client = authenticated_client(BusinessRole.ADMIN)

    first = client.post(
        "/api/v1/admin/product-images/",
        {
            "product": product.id,
            "image": SimpleUploadedFile("first.jpg", b"first", content_type="image/jpeg"),
            "is_primary": True,
        },
        format="multipart",
    )
    second = client.post(
        "/api/v1/admin/product-images/",
        {
            "product": product.id,
            "image": SimpleUploadedFile("second.webp", b"second", content_type="image/webp"),
            "is_primary": True,
        },
        format="multipart",
    )

    assert first.status_code == 201
    assert second.status_code == 201
    assert ProductImage.objects.filter(product=product, is_primary=True).count() == 1
    assert ProductImage.objects.get(pk=second.data["id"]).is_primary is True
