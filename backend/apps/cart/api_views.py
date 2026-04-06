from decimal import Decimal

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_http_methods

from apps.cart.models import Cart, CartItem
from apps.shops.models import Product, Shop
from apps.shops.serializers import product_dict
from apps.users.decorators import api_login_required
from apps.users.utils import json_error, parse_json


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@require_GET
@api_login_required
def api_cart(request):
    cart = _get_or_create_cart(request.user)
    items = []
    subtotal = Decimal("0")
    for line in cart.items.select_related("product", "product__shop"):
        if not line.product.is_available:
            continue
        pt = line.line_total()
        subtotal += pt
        d = product_dict(line.product)
        d["quantity"] = line.quantity
        d["line_total"] = str(pt)
        items.append(d)
    return JsonResponse({"items": items, "subtotal": str(subtotal)})


@require_http_methods(["POST"])
@api_login_required
def api_cart_add(request):
    data = parse_json(request)
    if data is None:
        return json_error("Invalid JSON")
    product_id = data.get("product_id")
    quantity = int(data.get("quantity") or 1)
    if quantity < 1:
        return json_error("quantity must be >= 1")
    product = Product.objects.filter(pk=product_id).select_related("shop").first()
    if not product or not product.is_available:
        return json_error("Product not available", 404)
    if not product.image:
        return json_error(
            "This product has no image. The outlet must upload a photo before it can be added to cart.",
            400,
        )
    if not product.shop.is_active or product.shop.approval_status != Shop.ApprovalStatus.APPROVED:
        return json_error("Shop not available", 400)
    cart = _get_or_create_cart(request.user)
    other_shops = (
        cart.items.exclude(product__shop_id=product.shop_id).exists()
    )
    if other_shops:
        return json_error("Cart contains items from another outlet. Clear cart first.", 409)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": quantity})
    if not created:
        item.quantity += quantity
        item.save()
    return JsonResponse(
        {
            "item": {
                "product_id": product.id,
                "quantity": item.quantity,
                "line_total": str(item.line_total()),
            }
        },
        status=200,
    )


@require_http_methods(["POST", "PATCH"])
@api_login_required
def api_cart_update_line(request):
    data = parse_json(request)
    if data is None:
        return json_error("Invalid JSON")
    product_id = data.get("product_id")
    quantity = int(data.get("quantity") or 0)
    cart = _get_or_create_cart(request.user)
    item = CartItem.objects.filter(cart=cart, product_id=product_id).first()
    if not item:
        return json_error("Line not found", 404)
    if quantity < 1:
        item.delete()
        return JsonResponse({"deleted": True})
    item.quantity = quantity
    item.save()
    return JsonResponse({"quantity": item.quantity, "line_total": str(item.line_total())})


@require_http_methods(["POST"])
@api_login_required
def api_cart_remove(request):
    data = parse_json(request)
    if data is None:
        return json_error("Invalid JSON")
    product_id = data.get("product_id")
    cart = _get_or_create_cart(request.user)
    CartItem.objects.filter(cart=cart, product_id=product_id).delete()
    return JsonResponse({"deleted": True})


@require_http_methods(["POST"])
@api_login_required
def api_cart_clear(request):
    cart = _get_or_create_cart(request.user)
    cart.items.all().delete()
    return JsonResponse({"cleared": True})
