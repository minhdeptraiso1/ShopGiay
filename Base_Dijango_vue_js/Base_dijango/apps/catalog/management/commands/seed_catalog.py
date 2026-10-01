from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.catalog.models import (
    Brand,
    Category,
    Color,
    InventoryBalance,
    Product,
    ProductImage,
    ProductVariant,
    Size,
    StockMovement,
)

PRODUCTS = (
    {
        "name": "Hải Duy Speed Pro 'Cyber Volt'",
        "slug": "speed-pro-cyber-volt",
        "brand": ("Hải Duy", "hai-duy"),
        "category": ("Giày chạy bộ", "running"),
        "color": ("Cyber Volt", "cyber-volt", "#A3E635"),
        "price": 2_650_000,
        "stock": 12,
        "image": (
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff"
            "?auto=format&fit=crop&w=1200&q=85"
        ),
        "description": (
            "Mẫu giày chạy hiệu năng cao với đệm phản hồi lực, thân giày thoáng khí "
            "và phối màu Cyber Volt nổi bật."
        ),
    },
    {
        "name": "Court Dominator 'High Impact'",
        "slug": "court-dominator",
        "brand": ("Jordan", "jordan"),
        "category": ("Giày bóng rổ", "basketball"),
        "color": ("High Impact", "high-impact", "#DC2626"),
        "price": 3_450_000,
        "stock": 9,
        "image": (
            "https://images.unsplash.com/photo-1608231387042-66d1773070a5"
            "?auto=format&fit=crop&w=1200&q=85"
        ),
        "description": (
            "Thiết kế cổ cao hỗ trợ khóa cổ chân, đế bám sân và bộ đệm ổn định "
            "cho các pha chuyển hướng tốc độ cao."
        ),
    },
    {
        "name": "Air Stealth Phantom 'Triple Black'",
        "slug": "air-stealth-phantom",
        "brand": ("Nike", "nike"),
        "category": ("Sneakers nam", "men"),
        "color": ("Triple Black", "triple-black", "#111827"),
        "price": 2_890_000,
        "stock": 14,
        "image": (
            "https://images.unsplash.com/photo-1552346154-21d32810aba3"
            "?auto=format&fit=crop&w=1200&q=85"
        ),
        "description": (
            "Sneaker tông đen linh hoạt cho phong cách hằng ngày, hoàn thiện với "
            "upper bền nhẹ và đế cao su chống trượt."
        ),
    },
    {
        "name": "Zoom Flight Vapor 'Electric Blue'",
        "slug": "zoom-flight-vapor",
        "brand": ("Nike", "nike"),
        "category": ("Giày chạy bộ", "running"),
        "color": ("Electric Blue", "electric-blue", "#0284C7"),
        "price": 2_450_000,
        "stock": 11,
        "image": (
            "https://images.unsplash.com/photo-1515955656352-a1fa3ffcd111"
            "?auto=format&fit=crop&w=1200&q=85"
        ),
        "description": (
            "Giày chạy nhẹ với form ôm chân, đệm êm và phối màu xanh điện dành cho "
            "tập luyện hằng ngày."
        ),
    },
    {
        "name": "Retro Heritage High 'Emerald Edition'",
        "slug": "retro-heritage-high",
        "brand": ("Jordan", "jordan"),
        "category": ("Sneakers mới", "new"),
        "color": ("Emerald", "emerald", "#059669"),
        "price": 3_100_000,
        "stock": 8,
        "image": (
            "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2"
            "?auto=format&fit=crop&w=1200&q=85"
        ),
        "description": (
            "Phom high-top cổ điển được làm mới bằng điểm nhấn xanh emerald, "
            "phù hợp với các outfit streetwear hiện đại."
        ),
    },
    {
        "name": "Matrix Knit Racer 'Pastel Cloud'",
        "slug": "matrix-knit-racer",
        "brand": ("Adidas", "adidas"),
        "category": ("Sneakers nữ", "women"),
        "color": ("Pastel Cloud", "pastel-cloud", "#F9A8D4"),
        "price": 1_950_000,
        "stock": 10,
        "image": (
            "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a"
            "?auto=format&fit=crop&w=1200&q=85"
        ),
        "description": (
            "Thân knit mềm nhẹ, thoáng khí và phối màu pastel dễ kết hợp cho nhịp sống năng động."
        ),
    },
    {
        "name": "Tất thể thao HD Performance Crew",
        "slug": "tat-hd-performance-crew",
        "brand": ("Hải Duy", "hai-duy"),
        "category": ("Tất & phụ kiện", "tat-phu-kien"),
        "product_type": Product.ProductType.ACCESSORY,
        "option_label": "Freesize 39–44",
        "price": 129_000,
        "stock": 60,
        "image": (
            "https://images.unsplash.com/photo-1582966772680-860e372bb558"
            "?auto=format&fit=crop&w=1200&q=85"
        ),
        "description": (
            "Tất cổ trung co giãn, thoáng khí và có đệm lòng bàn chân, phù hợp đi sneaker "
            "hoặc luyện tập hằng ngày."
        ),
    },
    {
        "name": "Bình xịt vệ sinh giày HD Clean 250 ml",
        "slug": "binh-xit-ve-sinh-hd-clean-250ml",
        "brand": ("Hải Duy Care", "hai-duy-care"),
        "category": ("Chăm sóc giày", "cham-soc-giay"),
        "product_type": Product.ProductType.CARE,
        "option_label": "Chai 250 ml",
        "price": 189_000,
        "stock": 45,
        "image": (
            "https://images.unsplash.com/photo-1556228578-8c89e6adf883"
            "?auto=format&fit=crop&w=1200&q=85"
        ),
        "description": (
            "Dung dịch vệ sinh dạng bọt dùng cho upper vải, da tổng hợp và đế cao su; "
            "đi kèm đầu xịt tiện dụng."
        ),
    },
    {
        "name": "Bộ bàn chải chăm sóc sneaker 3 món",
        "slug": "bo-ban-chai-sneaker-3-mon",
        "brand": ("Hải Duy Care", "hai-duy-care"),
        "category": ("Chăm sóc giày", "cham-soc-giay"),
        "product_type": Product.ProductType.CARE,
        "option_label": "Bộ 3 bàn chải",
        "price": 159_000,
        "stock": 35,
        "image": (
            "https://images.unsplash.com/photo-1608571423902-eed4a5ad8108"
            "?auto=format&fit=crop&w=1200&q=85"
        ),
        "description": (
            "Ba độ cứng lông bàn chải cho upper, viền đế và các khe khó làm sạch, "
            "phù hợp dùng cùng dung dịch vệ sinh giày."
        ),
    },
)

SIZES = ("39", "40", "41", "42", "43")


class Command(BaseCommand):
    help = "Tạo catalog demo idempotent cho môi trường phát triển."

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError("seed_catalog is disabled when DEBUG=False")

        created_products = 0
        created_variants = 0

        for spec in PRODUCTS:
            brand_name, brand_slug = spec["brand"]
            brand, _ = Brand.objects.update_or_create(
                slug=brand_slug,
                defaults={"name": brand_name, "is_active": True},
            )
            category_name, category_slug = spec["category"]
            category, _ = Category.objects.update_or_create(
                slug=category_slug,
                defaults={"name": category_name, "is_active": True},
            )
            color = None
            if "color" in spec:
                color_name, color_slug, hex_code = spec["color"]
                color, _ = Color.objects.update_or_create(
                    slug=color_slug,
                    defaults={"name": color_name, "hex_code": hex_code, "is_active": True},
                )
            product, product_created = Product.objects.update_or_create(
                slug=spec["slug"],
                defaults={
                    "brand": brand,
                    "category": category,
                    "name": spec["name"],
                    "description": spec["description"],
                    "product_type": spec.get("product_type", Product.ProductType.FOOTWEAR),
                    "status": Product.Status.PUBLISHED,
                    "published_at": timezone.now(),
                },
            )
            created_products += int(product_created)
            ProductImage.objects.get_or_create(
                product=product,
                is_primary=True,
                defaults={
                    "external_url": spec["image"],
                    "alt_text": spec["name"],
                    "sort_order": 0,
                },
            )

            labels = SIZES if product.product_type == Product.ProductType.FOOTWEAR else (None,)
            for sort_order, label in enumerate(labels, start=1):
                size = None
                if label is not None:
                    size, _ = Size.objects.update_or_create(
                        brand=brand,
                        label=label,
                        defaults={"sort_order": sort_order, "is_active": True},
                    )
                variant, variant_created = ProductVariant.objects.update_or_create(
                    sku=(
                        f"{spec['slug'].upper()}-{label}"
                        if label is not None
                        else spec["slug"].upper()
                    ),
                    defaults={
                        "product": product,
                        "size": size,
                        "color": color,
                        "option_label": spec.get("option_label", ""),
                        "price": spec["price"],
                        "currency": ProductVariant.Currency.VND,
                        "is_active": True,
                    },
                )
                created_variants += int(variant_created)
                balance, balance_created = InventoryBalance.objects.get_or_create(
                    variant=variant,
                    defaults={"quantity": spec["stock"]},
                )
                if balance_created:
                    StockMovement.objects.create(
                        variant=variant,
                        kind=StockMovement.Kind.RECEIPT,
                        delta=spec["stock"],
                        quantity_before=0,
                        quantity_after=spec["stock"],
                        reason="Khởi tạo dữ liệu catalog demo",
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Catalog sẵn sàng: {len(PRODUCTS)} sản phẩm "
                f"({created_products} mới), {created_variants} biến thể mới."
            )
        )
