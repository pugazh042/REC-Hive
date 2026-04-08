from django.contrib import admin
from django.urls import path, include

from api.views import (
    ShopDashboardView,
    ShopLoginView,
    ShopOrdersView,
    ShopProductDetailView,
    ShopProductListCreateView,
    ShopProfileView,
    ShopUpdateOrderStatusView,
)

urlpatterns = [

    # Admin
    path("admin/", admin.site.urls),

    # Customer APIs
    path("api/", include("api.urls")),

    # Shop APIs
    path("shop/login", ShopLoginView.as_view()),
    path("shop/orders", ShopOrdersView.as_view()),
    path("shop/update-order-status", ShopUpdateOrderStatusView.as_view()),
    path("shop/dashboard", ShopDashboardView.as_view()),
    path("shop/products", ShopProductListCreateView.as_view()),
    path("shop/products/<int:product_id>", ShopProductDetailView.as_view()),
    path("shop/profile", ShopProfileView.as_view()),

]