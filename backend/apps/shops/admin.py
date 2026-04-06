from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Product, Shop


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    prepopulated_fields = {"slug": ("name",)}


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "category", "is_open", "approval_status", "is_active")
    list_filter = ("approval_status", "is_active", "is_open")
    search_fields = ("name", "owner__email")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("workers",)
    inlines = [ProductInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("thumb", "name", "shop", "price", "is_available", "is_featured")
    list_filter = ("is_available", "is_featured", "shop")

    @admin.display(description="Image")
    def thumb(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="44" height="44" loading="lazy" '
                'style="border-radius:12px;object-fit:cover;border:1px solid #E0E0E0"/>',
                obj.image.url,
            )
        return "—"
