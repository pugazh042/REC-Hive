from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_http_methods

from apps.users.decorators import api_login_required, api_role_required
from apps.users.models import Favorite, Notification, Role, User
from apps.users.ratelimit import api_ratelimit
from apps.users.utils import json_error, parse_json


def _user_payload(user):
    role_slug = user.role.slug if user.role_id else None
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "phone": user.phone,
        "role": role_slug,
    }


@api_ratelimit("register", limit=10, window_seconds=3600)
@require_http_methods(["POST"])
def api_register(request):
    data = parse_json(request)
    if data is None:
        return json_error("Invalid JSON")
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    phone = (data.get("phone") or "").strip()
    first_name = (data.get("first_name") or "").strip()
    last_name = (data.get("last_name") or "").strip()
    if not email or not password:
        return json_error("email and password are required")
    if User.objects.filter(email=email).exists():
        return json_error("Email already registered", 409)
    user = User.objects.create_user(
        username=email,
        email=email,
        password=password,
        phone=phone,
        first_name=first_name,
        last_name=last_name,
    )
    user.refresh_from_db()
    login(request, user)
    return JsonResponse({"user": _user_payload(user)}, status=201)


@api_ratelimit("login", limit=25, window_seconds=300)
@require_http_methods(["POST"])
def api_login(request):
    data = parse_json(request)
    if data is None:
        return json_error("Invalid JSON")
    identifier = (data.get("email") or data.get("phone") or "").strip()
    password = data.get("password") or ""
    if not identifier or not password:
        return json_error("email or phone, and password are required")
    user = None
    if "@" in identifier:
        user = User.objects.filter(email__iexact=identifier).first()
    else:
        user = User.objects.filter(phone=identifier).first()
    if not user or user.is_blocked:
        return json_error("Invalid credentials", 401)
    auth_user = authenticate(request, username=user.email, password=password)
    if auth_user is None:
        return json_error("Invalid credentials", 401)
    login(request, auth_user)
    return JsonResponse({"user": _user_payload(auth_user)})


@require_http_methods(["POST"])
@api_login_required
def api_logout(request):
    logout(request)
    return JsonResponse({"detail": "logged out"})


@require_GET
@ensure_csrf_cookie
def api_csrf(request):
    return JsonResponse({"detail": "ok"})


@require_GET
@api_login_required
def api_me(request):
    return JsonResponse({"user": _user_payload(request.user)})


@require_http_methods(["PATCH", "PUT"])
@api_login_required
def api_profile_update(request):
    data = parse_json(request)
    if data is None:
        return json_error("Invalid JSON")
    u = request.user
    if "first_name" in data:
        u.first_name = (data.get("first_name") or "")[:150]
    if "last_name" in data:
        u.last_name = (data.get("last_name") or "")[:150]
    if "phone" in data:
        u.phone = (data.get("phone") or "")[:20]
    u.save()
    return JsonResponse({"user": _user_payload(u)})


@require_GET
@api_login_required
def api_favorites(request):
    from apps.shops.models import Product, Shop

    favs = Favorite.objects.filter(user=request.user).select_related("shop", "product", "product__shop")
    shops = []
    products = []
    for f in favs:
        if f.shop_id:
            shops.append(
                {
                    "id": f.shop.id,
                    "name": f.shop.name,
                    "slug": f.shop.slug,
                    "image": f.shop.image.url if f.shop.image else None,
                    "rating": str(f.shop.rating),
                    "is_open": f.shop.is_open,
                }
            )
        elif f.product_id:
            p = f.product
            products.append(
                {
                    "id": p.id,
                    "name": p.name,
                    "slug": p.slug,
                    "price": str(p.price),
                    "image": p.image.url if p.image else None,
                    "shop_slug": p.shop.slug,
                }
            )
    return JsonResponse({"shops": shops, "products": products})


@require_http_methods(["POST", "DELETE"])
@api_login_required
def api_favorite_toggle(request):
    data = parse_json(request) if request.body else {}
    if data is None:
        return json_error("Invalid JSON")
    shop_id = data.get("shop_id")
    product_id = data.get("product_id")
    if request.method == "POST":
        if shop_id:
            from apps.shops.models import Shop

            shop = Shop.objects.filter(pk=shop_id).first()
            if not shop:
                return json_error("Shop not found", 404)
            fav, created = Favorite.objects.get_or_create(user=request.user, shop=shop, defaults={"product": None})
            return JsonResponse({"created": created, "id": fav.id})
        if product_id:
            from apps.shops.models import Product

            product = Product.objects.filter(pk=product_id).first()
            if not product:
                return json_error("Product not found", 404)
            fav, created = Favorite.objects.get_or_create(
                user=request.user, product=product, defaults={"shop": None}
            )
            return JsonResponse({"created": created, "id": fav.id})
        return json_error("shop_id or product_id required")
    # DELETE
    if shop_id:
        Favorite.objects.filter(user=request.user, shop_id=shop_id).delete()
        return JsonResponse({"deleted": True})
    if product_id:
        Favorite.objects.filter(user=request.user, product_id=product_id).delete()
        return JsonResponse({"deleted": True})
    return json_error("shop_id or product_id required")


@require_GET
@api_role_required("admin")
def api_admin_users_list(request):
    from django.db.models import Count

    qs = User.objects.select_related("role").annotate(order_count=Count("orders")).order_by("-created_at")[:500]
    return JsonResponse(
        {
            "users": [
                {
                    "id": u.id,
                    "email": u.email,
                    "phone": u.phone,
                    "first_name": u.first_name,
                    "last_name": u.last_name,
                    "role": u.role.slug if u.role_id else None,
                    "is_active": u.is_active,
                    "is_blocked": u.is_blocked,
                    "is_staff": u.is_staff,
                    "order_count": u.order_count,
                    "created_at": u.created_at.isoformat(),
                }
                for u in qs
            ]
        }
    )


@require_http_methods(["PATCH", "PUT"])
@api_role_required("admin")
def api_admin_user_update(request, user_id):
    u = User.objects.filter(pk=user_id).first()
    if not u:
        return json_error("Not found", 404)
    data = parse_json(request)
    if data is None:
        return json_error("Invalid JSON")
    if "is_blocked" in data:
        u.is_blocked = bool(data["is_blocked"])
    if "is_active" in data:
        u.is_active = bool(data["is_active"])
    if "role_slug" in data:
        slug = data["role_slug"]
        role = Role.objects.filter(slug=slug).first()
        if role:
            u.role = role
    u.save()
    return JsonResponse({"user": _user_payload(u)})


@require_GET
@api_role_required("admin")
def api_admin_analytics(request):
    from datetime import timedelta

    from django.db.models import Sum
    from django.utils import timezone

    from apps.orders.models import Order, OrderItem
    from apps.shops.models import Product, Shop

    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    orders_today = Order.objects.filter(created_at__date=today).count()
    orders_week = Order.objects.filter(created_at__date__gte=week_ago).count()
    revenue = Order.objects.filter(status=Order.Status.COMPLETED).aggregate(s=Sum("total"))["s"] or 0
    top_items = (
        OrderItem.objects.values("product_name")
        .annotate(total_qty=Sum("quantity"))
        .order_by("-total_qty")[:10]
    )
    return JsonResponse(
        {
            "totals": {
                "users": User.objects.count(),
                "orders": Order.objects.count(),
                "revenue": str(revenue),
                "shops": Shop.objects.filter(is_active=True).count(),
                "products": Product.objects.count(),
            },
            "orders_today": orders_today,
            "orders_week": orders_week,
            "top_items": list(top_items),
        }
    )


@require_GET
@api_login_required
def api_notifications(request):
    qs = Notification.objects.filter(user=request.user)[:50]
    return JsonResponse(
        {
            "notifications": [
                {
                    "id": n.id,
                    "title": n.title,
                    "body": n.body,
                    "is_read": n.is_read,
                    "link": n.link,
                    "created_at": n.created_at.isoformat(),
                }
                for n in qs
            ]
        }
    )
