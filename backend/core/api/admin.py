from django.contrib import admin

from .models import (
    Cart,
    Shop,
    Category,
    Product,
    Order,
    OrderItem,
    Payment,
    ShopUser,
)

admin.site.register(Shop)

admin.site.register(Category)

admin.site.register(Product)

admin.site.register(Order)

admin.site.register(OrderItem)

admin.site.register(Payment)

admin.site.register(Cart)

admin.site.register(ShopUser)