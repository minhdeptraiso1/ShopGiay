from datetime import UTC, datetime
from decimal import Decimal

import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient

from apps.accounts.roles import BusinessRole
from apps.accounts.tests.factories import UserFactory
from apps.catalog.tests.factories import ProductFactory
from apps.operations.models import AuditLog
from apps.orders.models import Order

pytestmark = pytest.mark.django_db


def role_client(role: BusinessRole) -> tuple[APIClient, object]:
    user = UserFactory(is_staff=role in {BusinessRole.STAFF, BusinessRole.ADMIN})
    user.groups.add(Group.objects.get(name=role))
    client = APIClient()
    client.force_authenticate(user)
    return client, user


def paid_order(*, user, number: str, total: int) -> Order:
    return Order.objects.create(
        user=user,
        number=number,
        request_fingerprint="a" * 64,
        status=Order.Status.COMPLETED,
        payment_status=Order.PaymentStatus.PAID,
        subtotal=Decimal(total),
        shipping_fee=Decimal(0),
        discount_total=Decimal(0),
        total=Decimal(total),
        recipient_name="Khách hàng",
        phone_number="0901234567",
        province="Hà Nội",
        district="Ba Đình",
        ward="Điện Biên",
        street_address="1 Đường Mẫu",
    )


def test_dashboard_hides_finance_from_staff_and_returns_it_to_admin():
    staff_client, _ = role_client(BusinessRole.STAFF)
    admin_client, _ = role_client(BusinessRole.ADMIN)

    staff_response = staff_client.get("/api/v1/admin/dashboard/")
    admin_response = admin_client.get("/api/v1/admin/dashboard/")

    assert staff_response.status_code == 200
    assert staff_response.data["finance"] is None
    assert admin_response.status_code == 200
    assert admin_response.data["finance"]["revenue"] == "0"


def test_sales_report_is_admin_only_but_operational_reports_allow_staff():
    staff_client, _ = role_client(BusinessRole.STAFF)

    assert staff_client.get("/api/v1/admin/reports/sales/").status_code == 403
    assert staff_client.get("/api/v1/admin/reports/inventory/").status_code == 200
    assert staff_client.get("/api/v1/admin/reports/returns/").status_code == 200
    assert staff_client.get("/api/v1/admin/reports/recommendations/").status_code == 200


def test_sales_report_uses_vietnam_date_boundaries():
    admin_client, admin = role_client(BusinessRole.ADMIN)
    included = paid_order(user=admin, number="HD-IN", total=1_000_000)
    excluded = paid_order(user=admin, number="HD-OUT", total=2_000_000)
    Order.objects.filter(pk=included.pk).update(
        updated_at=datetime(2026, 10, 1, 17, 30, tzinfo=UTC)
    )
    Order.objects.filter(pk=excluded.pk).update(
        updated_at=datetime(2026, 10, 1, 16, 30, tzinfo=UTC)
    )

    response = admin_client.get(
        "/api/v1/admin/reports/sales/",
        {
            "start_date": "2026-10-02",
            "end_date": "2026-10-02",
            "timezone": "Asia/Ho_Chi_Minh",
        },
    )

    assert response.status_code == 200
    assert response.data["summary"]["revenue"] == "1000000"
    assert response.data["summary"]["paid_orders"] == 1


def test_admin_creates_and_deactivates_staff_without_privilege_escalation():
    admin_client, _ = role_client(BusinessRole.ADMIN)
    created = admin_client.post(
        "/api/v1/admin/staff/",
        {
            "email": "operator@example.com",
            "full_name": "Nhân viên vận hành",
            "password": "StrongPass!123",
            "roles": ["ADMIN"],
        },
        format="json",
    )

    assert created.status_code == 201
    assert created.data["roles"] == [BusinessRole.STAFF]
    updated = admin_client.patch(
        f"/api/v1/admin/staff/{created.data['id']}/", {"is_active": False}, format="json"
    )
    assert updated.status_code == 200
    assert updated.data["is_active"] is False


def test_tracked_change_creates_immutable_audit_log_visible_only_to_admin():
    ProductFactory()
    log = AuditLog.objects.filter(entity_type="catalog.product").latest("id")
    with pytest.raises(ValidationError):
        log.delete()

    staff_client, _ = role_client(BusinessRole.STAFF)
    admin_client, _ = role_client(BusinessRole.ADMIN)
    assert staff_client.get("/api/v1/admin/audit-logs/").status_code == 403
    response = admin_client.get("/api/v1/admin/audit-logs/?entity_type=catalog.product")
    assert response.status_code == 200
    assert response.data["results"][0]["entity_type"] == "catalog.product"


def test_csv_export_is_utf8_and_neutralizes_formula_cells():
    product = ProductFactory(name="=SUM(A1:A2)")
    variant = product.variants.create(sku="@DANGEROUS", price=10_000)
    from apps.catalog.models import InventoryBalance

    InventoryBalance.objects.create(variant=variant, quantity=0)
    staff_client, _ = role_client(BusinessRole.STAFF)

    response = staff_client.get("/api/v1/admin/reports/inventory/export/")

    body = response.content.decode("utf-8-sig")
    assert response.status_code == 200
    assert "'@DANGEROUS" in body
    assert "'=SUM(A1:A2)" in body
