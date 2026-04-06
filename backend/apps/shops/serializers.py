def shop_dict(shop, include_timing=True):
    d = {
        "id": shop.id,
        "owner_id": shop.owner_id,
        "name": shop.name,
        "slug": shop.slug,
        "description": shop.description,
        "rating": str(shop.rating),
        "is_open": shop.is_open,
        "is_active": shop.is_active,
        "approval_status": shop.approval_status,
        "category_id": shop.category_id,
        "category_name": shop.category.name if shop.category_id else None,
        "image": shop.image.url if shop.image else None,
        "banner": shop.banner.url if shop.banner else None,
        "pickup_location_hint": shop.pickup_location_hint,
    }
    if include_timing:
        d["open_time"] = shop.open_time.isoformat() if shop.open_time else None
        d["close_time"] = shop.close_time.isoformat() if shop.close_time else None
    return d


def product_dict(product):
    webp = None
    if getattr(product, "image_webp_id", None) and product.image_webp:
        webp = product.image_webp.url
    main = product.image.url if product.image else None
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "description": product.description,
        "price": str(product.price),
        "is_available": product.is_available,
        "is_featured": product.is_featured,
        "is_popular": product.is_popular,
        "shop_id": product.shop_id,
        "shop_name": product.shop.name,
        "shop_slug": product.shop.slug,
        "category_id": product.category_id,
        "image": webp or main,
        "image_fallback": main,
    }
