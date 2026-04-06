from functools import wraps

from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect


def role_required(*allowed_slugs):
    """Restrict view to users whose role.slug is in allowed_slugs."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            role = getattr(request.user, "role", None)
            slug = role.slug if role else None
            if slug not in allowed_slugs:
                return HttpResponseForbidden("You do not have access to this area.")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


def api_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication required"}, status=401)
        return view_func(request, *args, **kwargs)

    return _wrapped


def api_role_required(*allowed_slugs):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return JsonResponse({"detail": "Authentication required"}, status=401)
            role = getattr(request.user, "role", None)
            slug = role.slug if role else None
            if slug not in allowed_slugs and not request.user.is_superuser:
                return JsonResponse({"detail": "Forbidden"}, status=403)
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
