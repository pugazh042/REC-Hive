from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.views.decorators.http import require_GET, require_http_methods

from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem
from apps.shops.models import Shop
from apps.users.decorators import api_login_required, api_role_required
from apps.users.utils import json_error, parse_json


def _line_image_url(li):
    from django.apps import apps

    Product = apps.get_model("shops", "Product")
    if li.product_image:
        mu = settings.MEDIA_URL
        if not mu.endswith("/"):
            mu += "/"
        return mu + li.product_image.lstrip("/")
    try:
        p = Product.objects.only("image", "image_webp").get(pk=li.product_id)
        if getattr(p, "image_webp_id", None) and p.image_webp:
            return p.image_webp.url
        if p.image:
            return p.image.url
    except Exception:
        pass
    return None


def _notify_order_ready(order):
    from apps.users.models import Notification

    Notification.objects.create(
        user=order.user,
        title="Order ready for pickup",
        body=f"Order #{order.id} from {order.shop.name} is ready.",
        link=f"/orders/{order.id}/track/",
    )


def _order_dict(order):
    aw = order.assigned_worker
    return {
        "id": order.id,
        "status": order.status,
        "shop_id": order.shop_id,
        "shop_name": order.shop.name,
        "pickup_location": order.pickup_location,
        "estimated_ready_at": order.estimated_ready_at.isoformat() if order.estimated_ready_at else None,
        "subtotal": str(order.subtotal),
        "total": str(order.total),
        "special_instructions": order.special_instructions,
        "created_at": order.created_at.isoformat(),
        "assigned_worker_id": order.assigned_worker_id,
        "assigned_worker_email": aw.email if aw else None,
        "items": [
            {
                "product_id": li.product_id,
                "name": li.product_name,
                "quantity": li.quantity,
                "unit_price": str(li.unit_price),
                "line_total": str(li.line_total()),
                "special_instructions": li.special_instructions,
                "image": _line_image_url(li),
            }
            for li in order.items.all()
        ],
    }


def _persist_status(order, new_status):
    old = order.status
    order.status = new_status
    order.save(update_fields=["status", "updated_at"])
    if new_status == Order.Status.READY and old != Order.Status.READY:
        _notify_order_ready(order)
    return order


@require_http_methods(["POST"])
@api_login_required
def api_order_create(request):
    data = parse_json(request) or {}
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        return json_error("Cart is empty", 400)
    lines = list(cart.items.select_related("product", "product__shop"))
    shop_id = lines[0].product.shop_id
    for line in lines:
        if line.product.shop_id != shop_id:
            return json_error("Multiple outlets in cart", 400)
        if not line.product.is_available:
            return json_error(f"Unavailable: {line.product.name}", 400)
    shop = lines[0].product.shop
    pickup = data.get("pickup_location") or shop.pickup_location_hint or "Campus pickup counter"
    instructions = data.get("special_instructions") or ""
    subtotal = sum((line.line_total() for line in lines), Decimal("0"))
    order = Order.objects.create(
        user=request.user,
        shop=shop,
        status=Order.Status.ORDERED,
        pickup_location=pickup,
        special_instructions=instructions,
        subtotal=subtotal,
        total=subtotal,
        estimated_ready_at=timezone.now() + timedelta(minutes=20),
    )
    for line in lines:
        pr = line.product
        img_name = pr.image.name if pr.image else ""
        OrderItem.objects.create(
            order=order,
            product=pr,
            quantity=line.quantity,
            unit_price=pr.price,
            product_name=pr.name,
            product_image=img_name,
        )
    cart.items.all().delete()
    return JsonResponse({"order": _order_dict(order)}, status=201)


@require_http_methods(["POST"])
@api_login_required
def api_order_reorder(request):
    data = parse_json(request) or {}
    oid = data.get("order_id")
    if not oid:
        return json_error("order_id required", 400)
    order = (
        Order.objects.filter(pk=oid, user=request.user)
        .prefetch_related("items")
        .select_related("shop")
        .first()
    )
    if not order:
        return json_error("Not found", 404)
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    shop_id = None
    for li in order.items.all():
        pr = li.product
        if not pr.is_available:
            return json_error(f"Item unavailable: {pr.name}", 400)
        if shop_id is None:
            shop_id = pr.shop_id
        if pr.shop_id != shop_id:
            return json_error("Order contained multiple outlets", 400)
        CartItem.objects.update_or_create(
            cart=cart, product=pr, defaults={"quantity": li.quantity}
        )
    return JsonResponse({"detail": "Cart updated from order", "cart_id": cart.id})


@require_http_methods(["PATCH"])
@api_login_required
def api_order_assign_worker(request):
    data = parse_json(request)
    if data is None:
        return json_error("Invalid JSON", 400)
    order_id = data.get("order_id")
    worker_id = data.get("worker_id")
    if order_id is None:
        return json_error("order_id required", 400)
    order = Order.objects.filter(pk=order_id).select_related("shop").first()
    if not order:
        return json_error("Not found", 404)
    role = request.user.role.slug if request.user.role_id else None
    if request.user.is_superuser or role == "admin":
        if worker_id:
            from apps.users.models import User

            wu = User.objects.filter(pk=worker_id, role__slug="worker").first()
            if not wu:
                return json_error("Invalid worker", 400)
            order.assigned_worker = wu
        else:
            order.assigned_worker = None
        order.save(update_fields=["assigned_worker", "updated_at"])
        return JsonResponse({"order": _order_dict(order)})
    if role == "shopkeeper":
        if order.shop.owner_id != request.user.id:
            return json_error("Forbidden", 403)
        if worker_id:
            if not order.shop.workers.filter(pk=worker_id).exists():
                return json_error("Worker is not assigned to this shop", 400)
            from apps.users.models import User

            order.assigned_worker_id = worker_id
        else:
            order.assigned_worker = None
        order.save(update_fields=["assigned_worker", "updated_at"])
        return JsonResponse({"order": _order_dict(order)})
    return json_error("Forbidden", 403)


@require_GET
@api_login_required
def api_orders_list(request):
    qs = Order.objects.filter(user=request.user).select_related("shop").prefetch_related("items")
    return JsonResponse({"orders": [_order_dict(o) for o in qs]})


@require_GET
@api_login_required
def api_order_detail(request, order_id):
    order = Order.objects.filter(pk=order_id).select_related("shop", "assigned_worker").prefetch_related("items").first()
    if not order:
        return json_error("Not found", 404)
    role = request.user.role.slug if request.user.role_id else None
    if order.user_id != request.user.id and role not in ("admin", "shopkeeper", "worker"):
        return json_error("Forbidden", 403)
    if role == "shopkeeper":
        owned = Shop.objects.filter(owner=request.user, id=order.shop_id).exists()
        if not owned and not request.user.is_superuser:
            return json_error("Forbidden", 403)
    if role == "worker":
        if order.assigned_worker_id and order.assigned_worker_id != request.user.id and not request.user.is_superuser:
            if not request.user.assigned_shops.filter(id=order.shop_id).exists():
                return json_error("Forbidden", 403)
    return JsonResponse({"order": _order_dict(order)})


@require_http_methods(["PATCH"])
@api_login_required
def api_order_status(request):
    data = parse_json(request)
    if data is None:
        return json_error("Invalid JSON", 400)
    order_id = data.get("order_id")
    new_status = data.get("status")
    if not order_id or not new_status:
        return json_error("order_id and status required", 400)
    order = Order.objects.filter(pk=order_id).select_related("shop").first()
    if not order:
        return json_error("Not found", 404)
    role = request.user.role.slug if request.user.role_id else None
    valid = [c[0] for c in Order.Status.choices]
    if new_status not in valid:
        return json_error("Invalid status", 400)
    if role == "admin" or request.user.is_superuser:
        _persist_status(order, new_status)
        return JsonResponse({"order": _order_dict(order)})
    if role == "shopkeeper":
        if order.shop.owner_id != request.user.id:
            return json_error("Forbidden", 403)
        allowed = {
            Order.Status.ORDERED: [Order.Status.ACCEPTED, Order.Status.CANCELLED],
            Order.Status.ACCEPTED: [Order.Status.PREPARING, Order.Status.CANCELLED],
            Order.Status.PREPARING: [Order.Status.READY, Order.Status.CANCELLED],
            Order.Status.READY: [Order.Status.COMPLETED],
        }
        if new_status not in allowed.get(order.status, []):
            return json_error("Invalid transition", 400)
        _persist_status(order, new_status)
        return JsonResponse({"order": _order_dict(order)})
    if role == "worker":
        if order.assigned_worker_id and order.assigned_worker_id != request.user.id:
            return json_error("Forbidden", 403)
        if not request.user.assigned_shops.filter(id=order.shop_id).exists() and not request.user.is_superuser:
            return json_error("Forbidden", 403)
        allowed = {
            Order.Status.ACCEPTED: [Order.Status.PREPARING],
            Order.Status.PREPARING: [Order.Status.READY],
            Order.Status.READY: [Order.Status.COMPLETED],
        }
        if new_status not in allowed.get(order.status, []):
            return json_error("Invalid transition", 400)
        _persist_status(order, new_status)
        return JsonResponse({"order": _order_dict(order)})
    return json_error("Forbidden", 403)


@require_GET
@api_role_required("worker")
def api_worker_orders(request):
    shop_ids = request.user.assigned_shops.values_list("id", flat=True)
    qs = (
        Order.objects.filter(shop_id__in=shop_ids)
        .exclude(status__in=[Order.Status.COMPLETED, Order.Status.CANCELLED])
        .select_related("shop", "user", "assigned_worker")
        .prefetch_related("items")
        .order_by("-created_at")[:100]
    )
    return JsonResponse({"orders": [_order_dict(o) for o in qs]})


@require_GET
@api_role_required("admin", "shopkeeper")
def api_orders_shop_or_all(request):
    role = request.user.role.slug if request.user.role_id else None
    qs = Order.objects.all().select_related("shop", "user", "assigned_worker").prefetch_related("items")
    if role == "shopkeeper":
        qs = qs.filter(shop__owner=request.user)
    status = request.GET.get("status")
    if status:
        qs = qs.filter(status=status)
    qs = qs.order_by("-created_at")[:200]
    return JsonResponse({"orders": [_order_dict(o) for o in qs]})


@require_GET
@api_role_required("admin")
def api_admin_orders_analytics_sparkline(request):
    since = timezone.now().date() - timedelta(days=7)
    rows = (
        Order.objects.filter(created_at__date__gte=since)
        .annotate(d=TruncDate("created_at"))
        .values("d")
        .annotate(orders=Count("id"), revenue=Sum("total"))
        .order_by("d")
    )
    out = []
    for r in rows:
        d = r["d"]
        out.append(
            {
                "date": d.isoformat() if hasattr(d, "isoformat") else str(d),
                "orders": r["orders"],
                "revenue": str(r["revenue"] or 0),
            }
        )
    return JsonResponse({"daily": out})
