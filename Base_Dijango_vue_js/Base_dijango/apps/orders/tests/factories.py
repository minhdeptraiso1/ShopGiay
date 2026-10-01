import factory

from apps.accounts.tests.factories import AddressFactory, UserFactory
from apps.catalog.tests.factories import ProductVariantFactory
from apps.orders.models import Cart, CartItem


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    user = factory.SubFactory(UserFactory)


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    variant = factory.SubFactory(ProductVariantFactory, inventory=10)
    quantity = 1


__all__ = ["AddressFactory", "CartFactory", "CartItemFactory", "UserFactory"]
