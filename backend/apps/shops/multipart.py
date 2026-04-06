from decimal import Decimal, InvalidOperation


def post_int(request, key):
    v = request.POST.get(key)
    if v is None or v == "":
        return None
    try:
        return int(v)
    except ValueError:
        return None


def parse_product_post(request):
    """Common POST fields for multipart product forms."""
    return {
        "name": (request.POST.get("name") or "").strip(),
        "description": (request.POST.get("description") or "").strip(),
        "price_raw": request.POST.get("price"),
        "category_id": post_int(request, "category_id"),
        "shop_id": post_int(request, "shop_id"),
        "is_available": str(request.POST.get("is_available", "true")).lower() in ("1", "true", "yes", "on"),
        "is_featured": str(request.POST.get("is_featured", "false")).lower() in ("1", "true", "yes", "on"),
        "is_popular": str(request.POST.get("is_popular", "false")).lower() in ("1", "true", "yes", "on"),
    }


def parse_price(price_raw):
    try:
        return Decimal(str(price_raw))
    except (InvalidOperation, TypeError, ValueError):
        return None
