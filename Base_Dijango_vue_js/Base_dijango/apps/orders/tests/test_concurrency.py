import threading
from queue import Queue
from uuid import uuid4

import pytest
from django.contrib.auth.models import Group
from django.db import close_old_connections, connection

from apps.accounts.roles import BusinessRole
from apps.accounts.tests.factories import AddressFactory, UserFactory
from apps.catalog.tests.factories import ProductVariantFactory
from apps.orders.models import Cart, CartItem, Order
from apps.orders.services import InsufficientStockError, create_cod_order

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.mark.skipif(connection.vendor != "postgresql", reason="Cần PostgreSQL row-level locking")
def test_concurrent_orders_do_not_oversell_single_stock_unit():
    variant = ProductVariantFactory(inventory=1)
    group, _ = Group.objects.get_or_create(name=BusinessRole.CUSTOMER)
    requests = []
    for _ in range(2):
        user = UserFactory()
        user.groups.add(group)
        address = AddressFactory(user=user)
        cart = Cart.objects.create(user=user)
        item = CartItem.objects.create(cart=cart, variant=variant, quantity=1)
        requests.append((user, address.id, item.id))

    barrier = threading.Barrier(2)
    outcomes: Queue[str] = Queue()

    def submit(user, address_id: int, item_id: int) -> None:
        close_old_connections()
        barrier.wait()
        try:
            create_cod_order(
                user=user,
                address_id=address_id,
                cart_item_ids=[item_id],
                idempotency_key=uuid4(),
            )
        except InsufficientStockError:
            outcomes.put("insufficient")
        else:
            outcomes.put("created")
        finally:
            close_old_connections()

    threads = [threading.Thread(target=submit, args=request) for request in requests]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=10)

    assert all(not thread.is_alive() for thread in threads)
    assert sorted(outcomes.queue) == ["created", "insufficient"]
    assert Order.objects.count() == 1
    variant.inventory.refresh_from_db()
    assert variant.inventory.quantity == 0
