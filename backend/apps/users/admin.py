from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Favorite, Notification, Role, User


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("email", "username", "phone", "role", "is_blocked", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active", "is_blocked")
    search_fields = ("email", "username", "phone")

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        ("Profile", {"fields": ("first_name", "last_name", "phone", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_blocked", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2", "role"),
            },
        ),
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "shop", "product", "created_at")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "is_read", "created_at")
