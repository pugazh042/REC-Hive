from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        ORDERED = "ordered", "Ordered"
        ACCEPTED = "accepted", "Accepted"
        PREPARING = "preparing", "Preparing"
        READY = "ready", "Ready"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    shop = models.ForeignKey("shops.Shop", on_delete=models.PROTECT, related_name="orders")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ORDERED,
        db_index=True,
    )
    pickup_location = models.CharField(max_length=300, blank=True)
    estimated_ready_at = models.DateTimeField(null=True, blank=True)
    special_instructions = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    assigned_worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="worker_orders",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} — {self.shop.name}"


class OrderItem(TimeStampedModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("shops.Product", on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_name = models.CharField(max_length=200)
    """Relative path under MEDIA_ROOT (e.g. products/abc.jpg) at time of order."""
    product_image = models.CharField(max_length=512, blank=True)
    special_instructions = models.CharField(max_length=500, blank=True)

    def line_total(self):
        return self.quantity * self.unit_price
