from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from apps.users.decorators import role_required
from apps.users.models import User


def portal_redirect_name(user):
    if user.is_superuser:
        return "admin_dashboard"
    role = getattr(user, "role", None)
    slug = role.slug if role else "customer"
    return {
        "admin": "admin_dashboard",
        "shopkeeper": "shopkeeper_dashboard",
        "worker": "worker_orders",
        "customer": "home",
    }.get(slug, "home")


def splash(request):
    if request.user.is_authenticated:
        return redirect(reverse(portal_redirect_name(request.user)))
    return render(request, "customer/splash.html")


def onboarding(request):
    return render(request, "customer/onboarding.html")


@require_http_methods(["GET", "POST"])
def login_page(request):
    if request.user.is_authenticated:
        return redirect(reverse(portal_redirect_name(request.user)))
    if request.method == "POST":
        identifier = (request.POST.get("email") or request.POST.get("phone") or "").strip()
        password = request.POST.get("password") or ""
        user = None
        if "@" in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
        else:
            user = User.objects.filter(phone=identifier).first()
        if user and not user.is_blocked:
            auth_user = authenticate(request, username=user.email, password=password)
            if auth_user:
                login(request, auth_user)
                next_url = request.GET.get("next") or reverse(portal_redirect_name(auth_user))
                return redirect(next_url)
        return render(
            request,
            "customer/login.html",
            {"error": "Invalid credentials or account blocked."},
        )
    return render(request, "customer/login.html")


@require_http_methods(["GET", "POST"])
def signup_page(request):
    if request.user.is_authenticated:
        return redirect(reverse(portal_redirect_name(request.user)))
    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""
        phone = (request.POST.get("phone") or "").strip()
        if not email or not password:
            return render(request, "customer/signup.html", {"error": "Email and password required."})
        if User.objects.filter(email=email).exists():
            return render(request, "customer/signup.html", {"error": "Email already registered."})
        user = User.objects.create_user(username=email, email=email, password=password, phone=phone)
        user.refresh_from_db()
        login(request, user)
        return redirect("home")
    return render(request, "customer/signup.html")


@login_required
def logout_page(request):
    logout(request)
    return redirect("login")


@login_required
def home(request):
    role = getattr(request.user, "role", None)
    slug = role.slug if role else "customer"
    if slug != "customer" and not request.user.is_superuser:
        return redirect(reverse(portal_redirect_name(request.user)))
    return render(request, "customer/home.html")


@login_required
def outlets(request):
    return render(request, "customer/outlets.html")


@login_required
def outlet_detail(request, slug):
    return render(request, "customer/outlet_detail.html", {"shop_slug": slug})


@login_required
def product_detail(request, shop_slug, product_slug):
    return render(
        request,
        "customer/product_detail.html",
        {"shop_slug": shop_slug, "product_slug": product_slug},
    )


@login_required
def cart_page(request):
    return render(request, "customer/cart.html")


@login_required
def checkout_page(request):
    return render(request, "customer/checkout.html")


@login_required
def order_tracking(request, order_id):
    return render(request, "customer/order_tracking.html", {"order_id": order_id})


@login_required
def order_history(request):
    return render(request, "customer/order_history.html")


@login_required
def favorites_page(request):
    return render(request, "customer/favorites.html")


@login_required
def profile_page(request):
    return render(request, "customer/profile.html")


@login_required
@role_required("admin")
def admin_dashboard(request):
    return render(request, "admin/dashboard.html")


@login_required
@role_required("admin")
def admin_shops(request):
    return render(request, "admin/shops.html")


@login_required
@role_required("admin")
def admin_categories(request):
    return render(request, "admin/categories.html")


@login_required
@role_required("admin")
def admin_users(request):
    return render(request, "admin/users.html")


@login_required
@role_required("admin")
def admin_orders(request):
    return render(request, "admin/orders.html")


@login_required
@role_required("admin")
def admin_analytics(request):
    return render(request, "admin/analytics.html")


@login_required
@role_required("admin")
def admin_products(request):
    return render(request, "admin/products.html")


@login_required
@role_required("shopkeeper")
def shopkeeper_dashboard(request):
    return render(request, "shopkeeper/dashboard.html")


@login_required
@role_required("shopkeeper")
def shopkeeper_products(request):
    return render(request, "shopkeeper/products.html")


@login_required
@role_required("shopkeeper")
def shopkeeper_orders(request):
    return render(request, "shopkeeper/orders.html")


@login_required
@role_required("shopkeeper")
def shopkeeper_reports(request):
    return render(request, "shopkeeper/reports.html")


@login_required
@role_required("worker")
def worker_orders(request):
    return render(request, "worker/orders.html")
