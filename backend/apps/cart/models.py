from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Cart(TimeStampedModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
    )

    def __str__(self):
        return f"Cart #{self.pk} — {self.user.email}"


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("shops.Product", on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = [["cart", "product"]]

    def line_total(self):
        return self.quantity * self.product.price
