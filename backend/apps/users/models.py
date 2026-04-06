from django.contrib.auth.models import AbstractUser
from django.db import models


class TimeStampedModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Role(TimeStampedModel):
    """Application roles: customer, admin, shopkeeper, worker."""

    name = models.CharField(max_length=64, unique=True)
    slug = models.SlugField(max_length=64, unique=True)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, db_index=True)
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True,
    )
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


class Favorite(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    shop = models.ForeignKey(
        "shops.Shop",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="favorited_by",
    )
    product = models.ForeignKey(
        "shops.Product",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="favorited_by",
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(shop__isnull=False) | models.Q(product__isnull=False),
                name="favorite_shop_or_product",
            ),
            models.UniqueConstraint(
                fields=["user", "shop"],
                condition=models.Q(shop__isnull=False),
                name="unique_user_shop_favorite",
            ),
            models.UniqueConstraint(
                fields=["user", "product"],
                condition=models.Q(product__isnull=False),
                name="unique_user_product_favorite",
            ),
        ]


class Notification(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True)

    class Meta:
        ordering = ["-created_at"]
