import factory

from apps.catalog.models import (
    Brand,
    Category,
    Color,
    InventoryBalance,
    Product,
    ProductVariant,
    Size,
)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    name = factory.Sequence(lambda n: f"Danh mục {n}")
    slug = factory.Sequence(lambda n: f"danh-muc-{n}")


class BrandFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Brand

    name = factory.Sequence(lambda n: f"Thương hiệu {n}")
    slug = factory.Sequence(lambda n: f"thuong-hieu-{n}")


class ColorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Color

    name = factory.Sequence(lambda n: f"Màu {n}")
    slug = factory.Sequence(lambda n: f"mau-{n}")


class SizeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Size

    brand = factory.SubFactory(BrandFactory)
    label = factory.Sequence(lambda n: str(35 + n))


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    category = factory.SubFactory(CategoryFactory)
    brand = factory.SubFactory(BrandFactory)
    name = factory.Sequence(lambda n: f"Giày chạy bộ {n}")
    slug = factory.Sequence(lambda n: f"giay-chay-bo-{n}")
    status = Product.Status.PUBLISHED


class ProductVariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductVariant
        skip_postgeneration_save = True

    product = factory.SubFactory(ProductFactory)
    size = factory.LazyAttribute(lambda obj: SizeFactory(brand=obj.product.brand))
    color = factory.SubFactory(ColorFactory)
    sku = factory.Sequence(lambda n: f"SKU-{n:05d}")
    price = 1_500_000

    @factory.post_generation
    def inventory(self, create, extracted, **kwargs):
        if create:
            InventoryBalance.objects.create(variant=self, quantity=extracted or 0)
