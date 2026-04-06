from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("unit_price", "product_name", "product_image")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "shop", "status", "total", "created_at")
    list_filter = ("status", "shop")
    search_fields = ("user__email",)
    inlines = [OrderItemInline]
