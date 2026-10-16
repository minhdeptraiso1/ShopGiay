import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from apps.accounts.roles import BusinessRole
from apps.accounts.tests.factories import UserFactory
from apps.catalog.models import StockMovement
from apps.catalog.services import InsufficientStockError, adjust_inventory

from .factories import ProductVariantFactory

pytestmark = pytest.mark.django_db


def staff_client() -> tuple[APIClient, object]:
    user = UserFactory()
    group, _ = Group.objects.get_or_create(name=BusinessRole.STAFF)
    user.groups.add(group)
    client = APIClient()
    client.force_authenticate(user)
    return client, user


def test_staff_adjusts_inventory_and_movement_is_append_only():
    variant = ProductVariantFactory(inventory=3)
    client, _ = staff_client()

    response = client.post(
        f"/api/v1/admin/inventory/variants/{variant.id}/adjustments/",
        {"delta": 7, "kind": StockMovement.Kind.RECEIPT, "reason": "Phiếu nhập NK-001"},
        format="json",
    )

    assert response.status_code == 201
    assert response.data["quantity_before"] == 3
    assert response.data["quantity_after"] == 10
    movement = StockMovement.objects.get()
    movement.reason = "Không được sửa"
    with pytest.raises(ValidationError):
        movement.save()


def test_inventory_cannot_become_negative():
    variant = ProductVariantFactory(inventory=2)
    _, user = staff_client()

    with pytest.raises(InsufficientStockError):
        adjust_inventory(
            variant_id=variant.id,
            delta=-3,
            kind=StockMovement.Kind.ADJUSTMENT,
            reason="Kiểm kê",
            actor=user,
        )

    variant.inventory.refresh_from_db()
    assert variant.inventory.quantity == 2
    assert StockMovement.objects.count() == 0


def test_customer_cannot_adjust_inventory():
    variant = ProductVariantFactory(inventory=2)
    user = UserFactory()
    group, _ = Group.objects.get_or_create(name=BusinessRole.CUSTOMER)
    user.groups.add(group)
    client = APIClient()
    client.force_authenticate(user)

    response = client.post(
        f"/api/v1/admin/inventory/variants/{variant.id}/adjustments/",
        {"delta": 1, "kind": StockMovement.Kind.RECEIPT, "reason": "Không hợp lệ"},
        format="json",
    )

    assert response.status_code == 403


def test_staff_downloads_empty_inventory_template_and_current_sku_list():
    variant = ProductVariantFactory(sku="SAFE-SKU", inventory=7)
    variant.inventory.average_unit_cost = 125_000
    variant.inventory.save(update_fields=["average_unit_cost"])
    client, _ = staff_client()

    template = client.get("/api/v1/admin/inventory/receipts/template/")
    current = client.get("/api/v1/admin/inventory/receipts/export-current/")

    template_body = template.content.decode("utf-8-sig")
    current_body = current.content.decode("utf-8-sig")
    assert template.status_code == 200
    assert template_body.splitlines() == [
        "Mã SKU,Tồn kho hiện tại,Số lượng,Giá nhập/đơn vị,Ngày nhập,Nhà cung cấp,Ghi chú"
    ]
    assert current.status_code == 200
    assert "SAFE-SKU,7,,125000" in current_body


def test_staff_imports_only_filled_rows_from_current_sku_csv():
    selected = ProductVariantFactory(sku="SKU-SELECTED", inventory=7)
    untouched = ProductVariantFactory(sku="SKU-UNTOUCHED", inventory=4)
    client, _ = staff_client()
    content = (
        "Mã SKU,Tồn kho hiện tại,Số lượng,Giá nhập/đơn vị,Ngày nhập,Nhà cung cấp,Ghi chú\r\n"
        "SKU-SELECTED,7,2,120000,2026-10-02,Kho Hà Nội,Nhập bổ sung\r\n"
        "SKU-UNTOUCHED,4,,90000,2026-10-02,Kho Hà Nội,Không nhập\r\n"
    )
    upload = SimpleUploadedFile("nhap-kho.csv", content.encode("utf-8"), content_type="text/csv")

    response = client.post(
        "/api/v1/admin/inventory/receipts/import/", {"file": upload}, format="multipart"
    )

    assert response.status_code == 201
    selected.inventory.refresh_from_db()
    untouched.inventory.refresh_from_db()
    assert selected.inventory.quantity == 9
    assert untouched.inventory.quantity == 4
