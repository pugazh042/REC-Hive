from django.urls import path

from . import api_views

urlpatterns = [
    path("admin/users", api_views.api_admin_users_list),
    path("admin/users/<int:user_id>", api_views.api_admin_user_update),
    path("admin/analytics", api_views.api_admin_analytics),
    path("register", api_views.api_register),
    path("login", api_views.api_login),
    path("logout", api_views.api_logout),
    path("csrf", api_views.api_csrf),
    path("me", api_views.api_me),
    path("profile", api_views.api_profile_update),
    path("favorites", api_views.api_favorites),
    path("favorite", api_views.api_favorite_toggle),
    path("notifications", api_views.api_notifications),
]
