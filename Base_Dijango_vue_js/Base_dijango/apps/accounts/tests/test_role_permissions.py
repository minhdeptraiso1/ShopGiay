import pytest
from django.contrib.auth.models import Group

from apps.accounts.roles import BusinessRole
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
def test_admin_access_requires_staff_or_admin_business_role(api_client):
    customer = UserFactory()
    customer.groups.add(Group.objects.get(name=BusinessRole.CUSTOMER))
    api_client.force_authenticate(customer)
    assert api_client.get("/api/v1/admin/access/").status_code == 403

    customer.groups.set([Group.objects.get(name=BusinessRole.STAFF)])
    allowed = api_client.get("/api/v1/admin/access/")
    assert allowed.status_code == 200
    assert allowed.data["message"]


@pytest.mark.django_db
def test_admin_access_allows_superuser_and_rejects_guest(api_client):
    assert api_client.get("/api/v1/admin/access/").status_code == 401
    api_client.force_authenticate(UserFactory(is_staff=True, is_superuser=True))
    assert api_client.get("/api/v1/admin/access/").status_code == 200
