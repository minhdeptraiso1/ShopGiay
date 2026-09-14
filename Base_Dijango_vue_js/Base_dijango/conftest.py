import uuid

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    client = APIClient()
    client.defaults["REMOTE_ADDR"] = f"test-{uuid.uuid4()}"
    return client


@pytest.fixture
def csrf_client() -> APIClient:
    client = APIClient(enforce_csrf_checks=True)
    client.defaults["REMOTE_ADDR"] = f"test-{uuid.uuid4()}"
    return client
