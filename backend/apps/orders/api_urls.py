from django.urls import path

from . import api_views

urlpatterns = [
    path("order/create", api_views.api_order_create),
    path("order/status", api_views.api_order_status),
    path("orders/all", api_views.api_orders_shop_or_all),
    path("orders/kitchen", api_views.api_worker_orders),
    path("orders/<int:order_id>", api_views.api_order_detail),
    path("orders", api_views.api_orders_list),
]
