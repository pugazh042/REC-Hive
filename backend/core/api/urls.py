from django.urls import path

from .views import (
    CategoryListView,
    CreateOrderView,
    RegisterView,
    LoginView,
    ShopListView,
    ProductListView,
    CartView,
    OrderView,
    PaymentVerificationView,
    ShopDashboardView,
    ShopLoginView,
    ShopOrdersView,
    ShopProductDetailView,
    ShopProductListCreateView,
    ShopProfileView,
    ShopUpdateOrderStatusView,
    UserProfileView,
)

urlpatterns = [

    # Auth
    path("register/", RegisterView.as_view()),
    path("login/", LoginView.as_view()),
    path("profile/", UserProfileView.as_view()),

    # Shop browsing
    path("categories/", CategoryListView.as_view()),
    path("shops/", ShopListView.as_view()),
    path("products/", ProductListView.as_view()),

    # Cart
    path("cart/", CartView.as_view()),

    # Orders
    path("orders/", OrderView.as_view()),
    path("create-order/", CreateOrderView.as_view()),

    # Payment
    path(
        "payment/verify/",
        PaymentVerificationView.as_view()
    ),

    # Shop APIs (also exposed without /api in core.urls)
    path("shop/login/", ShopLoginView.as_view()),
    path("shop/orders/", ShopOrdersView.as_view()),
    path("shop/update-order-status/", ShopUpdateOrderStatusView.as_view()),
    path("shop/dashboard/", ShopDashboardView.as_view()),
    path("shop/products/", ShopProductListCreateView.as_view()),
    path("shop/products/<int:product_id>/", ShopProductDetailView.as_view()),
    path("shop/profile/", ShopProfileView.as_view()),

]