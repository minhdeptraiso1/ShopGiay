from uuid import uuid4

import pytest
from rest_framework.test import APIClient

from apps.catalog.models import Product, ProductEvent

from .factories import ProductFactory

pytestmark = pytest.mark.django_db


def test_guest_view_event_is_idempotent():
    product = ProductFactory()
    payload = {
        "client_event_id": str(uuid4()),
        "schema_version": 1,
        "event_type": ProductEvent.EventType.VIEW,
        "source": ProductEvent.Source.STOREFRONT,
        "product": product.id,
        "anonymous_id": str(uuid4()),
    }
    client = APIClient()

    first = client.post("/api/v1/events/", payload, format="json")
    second = client.post("/api/v1/events/", payload, format="json")

    assert first.status_code == 201
    assert second.status_code == 200
    assert ProductEvent.objects.count() == 1


def test_guest_event_requires_anonymous_id_and_published_product():
    draft = ProductFactory(status=Product.Status.DRAFT)
    response = APIClient().post(
        "/api/v1/events/",
        {
            "client_event_id": str(uuid4()),
            "schema_version": 1,
            "event_type": ProductEvent.EventType.VIEW,
            "source": ProductEvent.Source.SEARCH,
            "product": draft.id,
        },
        format="json",
    )

    assert response.status_code == 400
    assert ProductEvent.objects.count() == 0
