from django.conf import settings
from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.CharField(max_length=500, blank=True)
    icon = models.CharField(max_length=80, blank=True, help_text="Emoji or icon class name")

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:140]
        super().save(*args, **kwargs)


class Shop(TimeStampedModel):
    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_shops",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="shops",
    )
    image = models.ImageField(upload_to="shops/", blank=True, null=True)
    banner = models.ImageField(upload_to="shops/banners/", blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.5)
    is_open = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.APPROVED,
    )
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    pickup_location_hint = models.CharField(max_length=300, blank=True)

    workers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="assigned_shops",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)[:200]
            self.slug = base or "shop"
        super().save(*args, **kwargs)


class Product(TimeStampedModel):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    """Required for menu items (enforced at DB layer after backfill migration)."""
    image = models.ImageField(upload_to="products/")
    image_webp = models.ImageField(upload_to="products/webp/", blank=True, null=True)
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_popular = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        unique_together = [["shop", "slug"]]

    def __str__(self):
        return f"{self.name} @ {self.shop.name}"

    def save(self, *args, **kwargs):
        if getattr(self, "_skip_image_opt", False):
            self._skip_image_opt = False
            super().save(*args, **kwargs)
            return
        if not self.slug:
            self.slug = slugify(self.name)[:200] or "item"
        super().save(*args, **kwargs)
        if not self.image:
            return
        from apps.shops.image_utils import optimize_product_image

        if optimize_product_image(self, write_webp=True):
            self._skip_image_opt = True
            upd = ["image"]
            if self.image_webp and getattr(self.image_webp, "name", None):
                upd.append("image_webp")
            super().save(update_fields=upd)

    def effective_image_url(self):
        if self.image_webp_id and self.image_webp:
            return self.image_webp.url
        return self.image.url if self.image else ""
