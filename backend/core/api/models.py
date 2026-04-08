from django.db import models
from django.contrib.auth.models import User


# --------------------
# SHOP
# --------------------
class Shop(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    upi_id = models.CharField(max_length=120, blank=True)
    image_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# --------------------
# SHOP LOGIN USER
# --------------------
class ShopUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="shop_profile")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="shop_users")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "shop")

    def __str__(self):
        return f"{self.user.username} ({self.shop.name})"


# --------------------
# CATEGORY
# each shop has its own categories
# --------------------
class Category(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ("shop", "name")

    def __str__(self):
        return f"{self.shop.name} - {self.name}"


# --------------------
# PRODUCT
# belongs to category -> category belongs to shop
# --------------------
class Product(models.Model):

    TYPE_FOOD = "food"
    TYPE_PACKED = "packed"

    TYPE_CHOICES = [
        (TYPE_FOOD, "Food"),
        (TYPE_PACKED, "Packed Item"),
    ]

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    name = models.CharField(max_length=200)

    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)

    product_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default=TYPE_PACKED
    )

    price = models.DecimalField(max_digits=10, decimal_places=2)

    stock = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def shop(self):
        return self.category.shop

    def __str__(self):
        return self.name


# --------------------
# CART
# user adds items before placing order
# --------------------
class Cart(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart")

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} - {self.product.name} x{self.quantity}"


# --------------------
# ORDER
# created after payment initiated
# --------------------
class Order(models.Model):

    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_CANCELLED = "cancelled"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"


# --------------------
# ORDER ITEMS
# each shop updates its own items
# --------------------
class OrderItem(models.Model):

    SHOP_STATUS_PENDING = "pending"

    SHOP_STATUS_PREPARING = "preparing"   # food preparing

    SHOP_STATUS_READY = "ready"           # food ready

    SHOP_STATUS_AVAILABLE = "available"   # packed item available
    SHOP_STATUS_COMPLETED = "completed"   # delivered / picked up

    SHOP_STATUS_CHOICES = [

        (SHOP_STATUS_PENDING, "Pending"),

        (SHOP_STATUS_PREPARING, "Preparing"),

        (SHOP_STATUS_READY, "Ready"),

        (SHOP_STATUS_AVAILABLE, "Available for pickup"),
        (SHOP_STATUS_COMPLETED, "Complete / Pickup"),

    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    product = models.ForeignKey(Product, on_delete=models.PROTECT)

    quantity = models.PositiveIntegerField(default=1)

    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    shop_status = models.CharField(
        max_length=20,
        choices=SHOP_STATUS_CHOICES,
        default=SHOP_STATUS_PENDING
    )

    def shop(self):
        return self.product.category.shop

    def __str__(self):
        return f"Order #{self.order.id} - {self.product.name}"


# --------------------
# PAYMENT (UPI)
# --------------------
class Payment(models.Model):

    STATUS_PENDING = "pending"

    STATUS_VERIFIED = "verified"

    STATUS_FAILED = "failed"

    STATUS_CHOICES = [

        (STATUS_PENDING, "Pending"),

        (STATUS_VERIFIED, "Verified"),

        (STATUS_FAILED, "Failed"),

    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")

    payment_ref = models.CharField(max_length=120, unique=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    verified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.payment_ref}"