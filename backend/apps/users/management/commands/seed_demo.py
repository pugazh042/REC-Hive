import io
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFont

from apps.shops.models import Category, Product, Shop
from apps.users.models import Role, User


def _product_image_file(name, accent_rgb):
    """Generate a square JPEG placeholder (REC Hive theme)."""
    size = 512
    img = Image.new("RGB", (size, size), accent_rgb)
    draw = ImageDraw.Draw(img)
    margin = 24
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=32,
        outline=(255, 255, 255),
        width=6,
    )
    label = (name or "Item")[:18]
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - tw) // 2, (size - th) // 2), label, fill=(255, 255, 255), font=font)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=88, optimize=True)
    buf.seek(0)
    return ContentFile(buf.read(), name="seed.jpg")


class Command(BaseCommand):
    help = "Seed roles, categories, demo shops/products (optional demo users)."

    def handle(self, *args, **options):
        roles = [
            ("Customer", "customer", "Campus customer"),
            ("Admin", "admin", "Platform admin"),
            ("Shopkeeper", "shopkeeper", "Outlet owner"),
            ("Worker", "worker", "Kitchen / counter staff"),
        ]
        for name, slug, desc in roles:
            Role.objects.get_or_create(slug=slug, defaults={"name": name, "description": desc})

        cats = [
            ("Food", "food", "🍛"),
            ("Juice", "juice", "🧃"),
            ("Snacks", "snacks", "🍿"),
            ("Stationery", "stationery", "✏️"),
            ("Cafe", "cafe", "☕"),
            ("Mini Mart", "mini-mart", "🛒"),
        ]
        for name, slug, icon in cats:
            c, _ = Category.objects.get_or_create(slug=slug, defaults={"name": name, "icon": icon})

        admin = User.objects.filter(email="admin@rechive.edu").first()
        if not admin:
            admin = User.objects.create_superuser(
                email="admin@rechive.edu",
                username="admin@rechive.edu",
                password="admin123",
            )
            admin.refresh_from_db()
        ar = Role.objects.get(slug="admin")
        admin.role = ar
        admin.save(update_fields=["role"])

        sk_role = Role.objects.get(slug="shopkeeper")
        shopkeeper = User.objects.filter(email="shop@rechive.edu").first()
        if not shopkeeper:
            shopkeeper = User.objects.create_user(
                email="shop@rechive.edu",
                username="shop@rechive.edu",
                password="shop123",
                phone="9990001111",
            )
            shopkeeper.refresh_from_db()
        shopkeeper.role = sk_role
        shopkeeper.save(update_fields=["role"])

        wr = Role.objects.get(slug="worker")
        worker = User.objects.filter(email="kitchen@rechive.edu").first()
        if not worker:
            worker = User.objects.create_user(
                email="kitchen@rechive.edu",
                username="kitchen@rechive.edu",
                password="kitchen123",
            )
            worker.refresh_from_db()
        worker.role = wr
        worker.save(update_fields=["role"])

        food = Category.objects.get(slug="food")
        cafe = Category.objects.get(slug="cafe")

        tuck, _ = Shop.objects.get_or_create(
            slug="tuck-shop",
            defaults={
                "name": "REC Tuck Shop",
                "description": "Quick bites, chai, and rolls near the main block.",
                "owner": shopkeeper,
                "category": food,
                "rating": Decimal("4.6"),
                "is_open": True,
                "pickup_location_hint": "Main canteen counter — window A",
                "approval_status": Shop.ApprovalStatus.APPROVED,
            },
        )
        if not tuck.owner_id:
            tuck.owner = shopkeeper
            tuck.save(update_fields=["owner"])

        brew, _ = Shop.objects.get_or_create(
            slug="campus-brew",
            defaults={
                "name": "Campus Brew",
                "description": "Coffee, cold brew, and light snacks.",
                "owner": shopkeeper,
                "category": cafe,
                "rating": Decimal("4.8"),
                "is_open": True,
                "pickup_location_hint": "Library annex kiosk",
                "approval_status": Shop.ApprovalStatus.APPROVED,
            },
        )

        worker.assigned_shops.add(tuck, brew)

        demo_products = [
            (tuck, "Veg Roll", "veg-roll", Decimal("45"), True, True, (106, 27, 153)),
            (tuck, "Masala Chai", "masala-chai", Decimal("15"), True, True, (142, 36, 170)),
            (tuck, "Samosa Plate", "samosa-plate", Decimal("30"), True, False, (74, 20, 140)),
            (brew, "Cold Coffee", "cold-coffee", Decimal("60"), True, True, (156, 39, 176)),
            (brew, "Sandwich Combo", "sandwich-combo", Decimal("90"), True, False, (106, 27, 153)),
        ]
        for shop, name, slug, price, avail, pop, rgb in demo_products:
            p, _ = Product.objects.get_or_create(
                shop=shop,
                slug=slug,
                defaults={
                    "name": name,
                    "description": f"Fresh {name.lower()} from {shop.name}.",
                    "price": price,
                    "is_available": avail,
                    "is_popular": pop,
                    "category": shop.category,
                },
            )
            if not p.image:
                p.image.save(f"{slug}.jpg", _product_image_file(name, rgb), save=True)

        cust = User.objects.filter(email="student@rechive.edu").first()
        if not cust:
            cust = User.objects.create_user(
                email="student@rechive.edu",
                username="student@rechive.edu",
                password="student123",
                phone="9880012345",
            )
            cust.refresh_from_db()
        cust.role = Role.objects.get(slug="customer")
        cust.save(update_fields=["role"])

        self.stdout.write(self.style.SUCCESS("Seed complete. Try admin@rechive.edu / admin123"))
