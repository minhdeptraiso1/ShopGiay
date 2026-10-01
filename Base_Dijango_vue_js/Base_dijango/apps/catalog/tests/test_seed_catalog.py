import pytest
from django.core.management import call_command
from django.test import override_settings
from rest_framework.test import APIClient

from apps.catalog.models import (
    InventoryBalance,
    Product,
    ProductImage,
    ProductVariant,
    StockMovement,
)
from apps.catalog.selectors import list_public_products

pytestmark = pytest.mark.django_db


@override_settings(DEBUG=True)
def test_seed_catalog_is_idempotent_and_preserves_existing_inventory():
    call_command("seed_catalog")
    variant = ProductVariant.objects.get(sku="SPEED-PRO-CYBER-VOLT-39")
    variant.inventory.quantity = 3
    variant.inventory.save(update_fields=["quantity"])

    call_command("seed_catalog")

    assert Product.objects.filter(status=Product.Status.PUBLISHED).count() == 9
    assert ProductVariant.objects.count() == 33
    assert InventoryBalance.objects.count() == 33
    assert StockMovement.objects.count() == 33
    assert ProductImage.objects.filter(external_url__startswith="https://").count() == 9
    variant.inventory.refresh_from_db()
    assert variant.inventory.quantity == 3
    assert list_public_products().count() == 9
    care_variant = ProductVariant.objects.get(sku="BINH-XIT-VE-SINH-HD-CLEAN-250ML")
    assert care_variant.size is None
    assert care_variant.color is None
    assert care_variant.option_label == "Chai 250 ml"

    response = APIClient().get("/api/v1/products/")
    assert response.status_code == 200
    assert response.data["count"] == 9, response.data
    assert response.data["results"][0]["primary_image"]["image_url"].startswith("https://")
