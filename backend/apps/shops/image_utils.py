"""Server-side image optimization for product photos (Pillow)."""
import io
import os

from django.core.files.base import ContentFile


MAX_DIMENSION = 1024
JPEG_QUALITY = 85
WEBP_QUALITY = 82


def optimize_product_image(product, write_webp: bool = True) -> bool:
    """
    Resize (max edge MAX_DIMENSION), JPEG re-encode. Optional parallel WebP.
    """
    from PIL import Image

    if not product.image:
        return False
    try:
        path = product.image.path
    except Exception:
        return False
    if not path or not os.path.isfile(path):
        return False
    try:
        img = Image.open(path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        else:
            img = img.convert("RGB")
        w, h = img.size
        if w > MAX_DIMENSION or h > MAX_DIMENSION:
            img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        buf.seek(0)
        stem = os.path.splitext(os.path.basename(product.image.name))[0]
        new_name = f"{stem}.jpg"
        product.image.save(new_name, ContentFile(buf.read()), save=False)

        if write_webp and getattr(product, "image_webp", None) is not None:
            try:
                wbuf = io.BytesIO()
                img.save(wbuf, format="WEBP", quality=WEBP_QUALITY, method=4)
                wbuf.seek(0)
                product.image_webp.save(f"{stem}.webp", ContentFile(wbuf.read()), save=False)
            except Exception:
                pass
        return True
    except Exception:
        return False
