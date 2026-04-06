from django.urls import path

from . import api_views

urlpatterns = [
    path("cart", api_views.api_cart),
    path("cart/add", api_views.api_cart_add),
    path("cart/update", api_views.api_cart_update_line),
    path("cart/remove", api_views.api_cart_remove),
    path("cart/clear", api_views.api_cart_clear),
]
