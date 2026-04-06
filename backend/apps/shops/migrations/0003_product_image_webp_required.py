import io

from django.core.files.base import ContentFile
from django.db import migrations, models
def backfill_product_images(apps, schema_editor):
    Product = apps.get_model("shops", "Product")
    from PIL import Image

    for p in Product.objects.iterator():
        has_img = False
        try:
            has_img = bool(p.image and getattr(p.image, "name", None))
        except Exception:
            has_img = False
        if has_img:
            continue
        im = Image.new("RGB", (128, 128), (106, 27, 153))
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=82)
        buf.seek(0)
        p.image.save(f"backfill_{p.pk}.jpg", ContentFile(buf.read()), save=True)


def noop_backfill(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("shops", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="image_webp",
            field=models.ImageField(blank=True, null=True, upload_to="products/webp/"),
        ),
        migrations.RunPython(backfill_product_images, noop_backfill),
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.ImageField(upload_to="products/"),
        ),
    ]
