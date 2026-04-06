from django.urls import path

from . import api_views

urlpatterns = [
    path("shops", api_views.api_shops),
    path("shops/<slug:slug>", api_views.api_shop_detail),
    path("products", api_views.api_products),
    path("shops/<slug:shop_slug>/products/<slug:product_slug>", api_views.api_product_detail),
    path("categories", api_views.api_categories),
    path("admin/shops/list", api_views.api_admin_shops_list),
    path("admin/shops", api_views.api_admin_shop_mutate),
    path("admin/shops/<int:shop_id>", api_views.api_admin_shop_mutate),
    path("admin/categories", api_views.api_admin_category_mutate),
    path("admin/categories/<int:category_id>", api_views.api_admin_category_mutate),
    path("admin/products", api_views.api_admin_products),
    path("admin/products/<int:product_id>", api_views.api_admin_product_mutate),
    path("shopkeeper/products", api_views.api_shopkeeper_product_mutate),
    path("shopkeeper/products/<int:product_id>", api_views.api_shopkeeper_product_mutate),
]
