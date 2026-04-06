from django.conf import settings


def portal_context(request):
    """Expose role slug and media URL to all templates."""
    role_slug = None
    if request.user.is_authenticated:
        r = getattr(request.user, "role", None)
        role_slug = r.slug if r else None
    return {
        "current_role_slug": role_slug,
        "media_url": settings.MEDIA_URL,
    }
