from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_http_methods

from apps.shops.models import Category, Product, Shop
from apps.shops.multipart import parse_price, parse_product_post
from apps.shops.serializers import product_dict, shop_dict
from apps.users.decorators import api_login_required, api_role_required
from apps.users.utils import json_error, parse_json


@require_GET
def api_shops(request):
    qs = Shop.objects.filter(is_active=True, approval_status=Shop.ApprovalStatus.APPROVED).select_related(
        "category"
    )
    category_slug = request.GET.get("category")
    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    q = request.GET.get("q")
    if q:
        qs = qs.filter(name__icontains=q)
    return JsonResponse({"shops": [shop_dict(s) for s in qs]})


@require_GET
def api_shop_detail(request, slug):
    shop = get_object_or_404(
        Shop.objects.select_related("category"),
        slug=slug,
        is_active=True,
        approval_status=Shop.ApprovalStatus.APPROVED,
    )
    return JsonResponse({"shop": shop_dict(shop)})


@require_GET
def api_products(request):
    qs = Product.objects.filter(shop__is_active=True, shop__approval_status=Shop.ApprovalStatus.APPROVED).select_related(
        "shop", "category"
    )
    shop_slug = request.GET.get("shop")
    if shop_slug:
        qs = qs.filter(shop__slug=shop_slug)
    category_slug = request.GET.get("category")
    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    featured = request.GET.get("featured")
    if featured in ("1", "true", "yes"):
        qs = qs.filter(is_featured=True)
    popular = request.GET.get("popular")
    if popular in ("1", "true", "yes"):
        qs = qs.filter(is_popular=True)
    q = request.GET.get("q")
    if q:
        qs = qs.filter(name__icontains=q)
    return JsonResponse({"products": [product_dict(p) for p in qs]})


@require_GET
def api_product_detail(request, shop_slug, product_slug):
    product = get_object_or_404(
        Product.objects.select_related("shop", "category"),
        shop__slug=shop_slug,
        slug=product_slug,
    )
    return JsonResponse({"product": product_dict(product)})


@require_GET
def api_categories(request):
    cats = Category.objects.all().order_by("name")
    return JsonResponse(
        {
            "categories": [
                {"id": c.id, "name": c.name, "slug": c.slug, "icon": c.icon, "description": c.description}
                for c in cats
            ]
        }
    )


@require_http_methods(["POST", "PATCH", "DELETE"])
@api_role_required("admin")
def api_admin_shop_mutate(request, shop_id=None):
    if request.method == "POST":
        data = parse_json(request)
        if data is None:
            return json_error("Invalid JSON")
        name = (data.get("name") or "").strip()
        if not name:
            return json_error("name required")
        shop = Shop.objects.create(
            name=name,
            description=data.get("description") or "",
            owner_id=data.get("owner_id"),
            category_id=data.get("category_id"),
            is_open=bool(data.get("is_open", True)),
            pickup_location_hint=data.get("pickup_location_hint") or "",
        )
        return JsonResponse({"shop": shop_dict(shop)}, status=201)
    if request.method == "PATCH" and shop_id:
        shop = Shop.objects.filter(pk=shop_id).first()
        if not shop:
            return json_error("Not found", 404)
        data = parse_json(request)
        if data is None:
            return json_error("Invalid JSON")
        for field in ("name", "description", "pickup_location_hint"):
            if field in data:
                setattr(shop, field, data[field] or "")
        if "is_open" in data:
            shop.is_open = bool(data["is_open"])
        if "is_active" in data:
            shop.is_active = bool(data["is_active"])
        if "approval_status" in data:
            shop.approval_status = data["approval_status"]
        if "category_id" in data:
            shop.category_id = data["category_id"]
        if "owner_id" in data:
            shop.owner_id = data["owner_id"]
        shop.save()
        return JsonResponse({"shop": shop_dict(shop)})
    if request.method == "DELETE" and shop_id:
        Shop.objects.filter(pk=shop_id).delete()
        return JsonResponse({"deleted": True})
    return json_error("Invalid request", 400)


@require_http_methods(["POST", "PATCH", "DELETE"])
@api_role_required("admin")
def api_admin_category_mutate(request, category_id=None):
    if request.method == "POST":
        data = parse_json(request)
        if data is None:
            return json_error("Invalid JSON")
        name = (data.get("name") or "").strip()
        if not name:
            return json_error("name required")
        c = Category.objects.create(
            name=name,
            description=data.get("description") or "",
            icon=data.get("icon") or "",
        )
        return JsonResponse(
            {"category": {"id": c.id, "name": c.name, "slug": c.slug, "icon": c.icon}}, status=201
        )
    if request.method == "PATCH" and category_id:
        c = Category.objects.filter(pk=category_id).first()
        if not c:
            return json_error("Not found", 404)
        data = parse_json(request)
        if data is None:
            return json_error("Invalid JSON")
        if "name" in data:
            c.name = data["name"]
        if "description" in data:
            c.description = data["description"] or ""
        if "icon" in data:
            c.icon = data["icon"] or ""
        c.save()
        return JsonResponse({"category": {"id": c.id, "name": c.name, "slug": c.slug, "icon": c.icon}})
    if request.method == "DELETE" and category_id:
        Category.objects.filter(pk=category_id).delete()
        return JsonResponse({"deleted": True})
    return json_error("Invalid request", 400)


def _is_multipart(request):
    ct = (request.content_type or "").lower()
    return "multipart/form-data" in ct


@require_GET
@api_role_required("admin")
def api_admin_shops_list(request):
    qs = Shop.objects.select_related("category").order_by("name")
    return JsonResponse(
        {
            "shops": [
                {
                    "id": s.id,
                    "name": s.name,
                    "slug": s.slug,
                    "is_active": s.is_active,
                    "is_open": s.is_open,
                    "approval_status": s.approval_status,
                }
                for s in qs
            ]
        }
    )


@require_http_methods(["GET", "POST"])
@api_role_required("admin")
def api_admin_products(request):
    if request.method == "GET":
        qs = Product.objects.select_related("shop", "category").order_by("-updated_at")[:800]
        rows = []
        for p in qs:
            d = product_dict(p)
            d["shop_id"] = p.shop_id
            d["category_name"] = p.category.name if p.category_id else None
            rows.append(d)
        return JsonResponse({"products": rows})
    if request.method == "POST":
        if not _is_multipart(request):
            return json_error("Use multipart/form-data including a required image file", 400)
        fields = parse_product_post(request)
        if not fields["name"]:
            return json_error("name is required", 400)
        price = parse_price(fields["price_raw"])
        if price is None:
            return json_error("valid price is required", 400)
        sid = fields["shop_id"]
        if not sid:
            return json_error("shop_id is required", 400)
        shop = Shop.objects.filter(pk=sid).first()
        if not shop:
            return json_error("shop not found", 404)
        img = request.FILES.get("image")
        if not img or not getattr(img, "name", ""):
            return json_error("image file is required", 400)
        p = Product(
            shop=shop,
            name=fields["name"],
            description=fields["description"],
            price=price,
            category_id=fields["category_id"],
            is_available=fields["is_available"],
            is_featured=fields["is_featured"],
            is_popular=fields["is_popular"],
        )
        p.image.save(img.name, img, save=False)
        p.save()
        return JsonResponse({"product": product_dict(p)}, status=201)
    return json_error("Method not allowed", 405)


@require_http_methods(["PATCH", "DELETE"])
@api_role_required("admin")
def api_admin_product_mutate(request, product_id=None):
    if request.method == "PATCH" and product_id:
        p = Product.objects.filter(pk=product_id).select_related("shop").first()
        if not p:
            return json_error("Not found", 404)
        if _is_multipart(request):
            fields = parse_product_post(request)
            if fields["name"]:
                p.name = fields["name"]
            if fields["description"] is not None:
                p.description = fields["description"]
            pr = parse_price(fields["price_raw"])
            if pr is not None:
                p.price = pr
            if fields["category_id"] is not None:
                p.category_id = fields["category_id"]
            p.is_available = fields["is_available"]
            p.is_featured = fields["is_featured"]
            p.is_popular = fields["is_popular"]
            img = request.FILES.get("image")
            if img and getattr(img, "name", ""):
                p.image.save(img.name, img, save=False)
            if not p.image:
                return json_error("image is required; upload a product photo", 400)
            p.save()
            return JsonResponse({"product": product_dict(p)})
        data = parse_json(request)
        if data is None:
            return json_error("Invalid JSON", 400)
        if "name" in data:
            p.name = (data.get("name") or "").strip() or p.name
        if "description" in data:
            p.description = data.get("description") or ""
        if "price" in data:
            pr = parse_price(data.get("price"))
            if pr is None:
                return json_error("valid price required", 400)
            p.price = pr
        if "category_id" in data:
            p.category_id = data["category_id"]
        if "is_available" in data:
            p.is_available = bool(data["is_available"])
        if "is_featured" in data:
            p.is_featured = bool(data["is_featured"])
        if "is_popular" in data:
            p.is_popular = bool(data["is_popular"])
        p.save()
        if not p.image:
            return json_error("image is required; edit with multipart to upload photo", 400)
        return JsonResponse({"product": product_dict(p)})
    if request.method == "DELETE" and product_id:
        Product.objects.filter(pk=product_id).delete()
        return JsonResponse({"deleted": True})
    return json_error("Invalid request", 400)


@require_http_methods(["POST", "PATCH", "DELETE"])
@api_login_required
def api_shopkeeper_product_mutate(request, product_id=None):
    if not request.user.role or request.user.role.slug != "shopkeeper":
        if not request.user.is_superuser:
            return json_error("Forbidden", 403)
    owned = Shop.objects.filter(owner=request.user)
    if not owned.exists():
        return json_error("No shop assigned", 403)
    shop = owned.first()
    if request.method == "POST":
        if not _is_multipart(request):
            return json_error("Use multipart/form-data with required image file", 400)
        fields = parse_product_post(request)
        if not fields["name"]:
            return json_error("name is required", 400)
        price = parse_price(fields["price_raw"])
        if price is None:
            return json_error("valid price is required", 400)
        img = request.FILES.get("image")
        if not img or not getattr(img, "name", ""):
            return json_error("image file is required", 400)
        p = Product(
            shop=shop,
            name=fields["name"],
            description=fields["description"],
            price=price,
            category_id=fields["category_id"],
            is_available=fields["is_available"],
            is_featured=fields["is_featured"],
            is_popular=fields["is_popular"],
        )
        p.image.save(img.name, img, save=False)
        p.save()
        return JsonResponse({"product": product_dict(p)}, status=201)
    if request.method == "PATCH" and product_id:
        p = Product.objects.filter(pk=product_id, shop=shop).first()
        if not p:
            return json_error("Not found", 404)
        if _is_multipart(request):
            fields = parse_product_post(request)
            if fields["name"]:
                p.name = fields["name"]
            if fields["description"] is not None:
                p.description = fields["description"]
            pr = parse_price(fields["price_raw"])
            if pr is not None:
                p.price = pr
            if fields["category_id"] is not None:
                p.category_id = fields["category_id"]
            p.is_available = fields["is_available"]
            p.is_featured = fields["is_featured"]
            p.is_popular = fields["is_popular"]
            img = request.FILES.get("image")
            if img and getattr(img, "name", ""):
                p.image.save(img.name, img, save=False)
            if not p.image:
                return json_error("image is required; upload a product photo", 400)
            p.save()
            return JsonResponse({"product": product_dict(p)})
        data = parse_json(request)
        if data is None:
            return json_error("Invalid JSON", 400)
        if "name" in data:
            p.name = (data.get("name") or "").strip() or p.name
        if "description" in data:
            p.description = data.get("description") or ""
        if "price" in data:
            pr = parse_price(data.get("price"))
            if pr is None:
                return json_error("valid price required", 400)
            p.price = pr
        if "category_id" in data:
            p.category_id = data["category_id"]
        if "is_available" in data:
            p.is_available = bool(data["is_available"])
        if "is_featured" in data:
            p.is_featured = bool(data["is_featured"])
        if "is_popular" in data:
            p.is_popular = bool(data["is_popular"])
        p.save()
        if not p.image:
            return json_error("image is required", 400)
        return JsonResponse({"product": product_dict(p)})
    if request.method == "DELETE" and product_id:
        Product.objects.filter(pk=product_id, shop=shop).delete()
        return JsonResponse({"deleted": True})
    return json_error("Invalid request", 400)
