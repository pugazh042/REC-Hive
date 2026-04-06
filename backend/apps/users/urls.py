from django.urls import path

from . import views

urlpatterns = [
    path("", views.splash, name="splash"),
    path("onboarding/", views.onboarding, name="onboarding"),
    path("login/", views.login_page, name="login"),
    path("signup/", views.signup_page, name="signup"),
    path("logout/", views.logout_page, name="logout"),
    path("home/", views.home, name="home"),
    path("outlets/", views.outlets, name="outlets"),
    path("outlets/<slug:slug>/", views.outlet_detail, name="outlet_detail"),
    path("outlets/<slug:shop_slug>/p/<slug:product_slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_page, name="cart"),
    path("checkout/", views.checkout_page, name="checkout"),
    path("orders/<int:order_id>/track/", views.order_tracking, name="order_tracking"),
    path("orders/history/", views.order_history, name="order_history"),
    path("favorites/", views.favorites_page, name="favorites"),
    path("profile/", views.profile_page, name="profile"),
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-panel/shops/", views.admin_shops, name="admin_shops"),
    path("admin-panel/categories/", views.admin_categories, name="admin_categories"),
    path("admin-panel/users/", views.admin_users, name="admin_users"),
    path("admin-panel/orders/", views.admin_orders, name="admin_orders"),
    path("admin-panel/products/", views.admin_products, name="admin_products"),
    path("admin-panel/analytics/", views.admin_analytics, name="admin_analytics"),
    path("shopkeeper/", views.shopkeeper_dashboard, name="shopkeeper_dashboard"),
    path("shopkeeper/products/", views.shopkeeper_products, name="shopkeeper_products"),
    path("shopkeeper/orders/", views.shopkeeper_orders, name="shopkeeper_orders"),
    path("shopkeeper/reports/", views.shopkeeper_reports, name="shopkeeper_reports"),
    path("kitchen/", views.worker_orders, name="worker_orders"),
]
