import factory
from django.contrib.auth import get_user_model

from apps.accounts.models import Address


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    full_name = factory.Faker("name")
    password = "StrongPass!123"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return model_class.objects.create_user(*args, **kwargs)


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Address

    user = factory.SubFactory(UserFactory)
    recipient_name = factory.Faker("name")
    phone_number = "0901234567"
    province = "Hà Nội"
    district = "Ba Đình"
    ward = "Điện Biên"
    street_address = factory.Sequence(lambda n: f"Số {n + 1} Đường Mẫu")
    is_default = False
