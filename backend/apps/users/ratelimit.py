"""Simple IP-based rate limiting for sensitive API views (uses Django cache)."""
import functools
import hashlib

from django.core.cache import cache
from django.http import JsonResponse


def get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()[:64]
    return (request.META.get("REMOTE_ADDR") or "unknown")[:64]


def api_ratelimit(prefix: str, limit: int = 30, window_seconds: int = 60):
    """
    Block after `limit` hits per IP per `window_seconds`.
    Use conservative limits on auth; stricter on uploads in production via env.
    """

    def decorator(view_func):
        @functools.wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            ip = get_client_ip(request)
            key = f"rl:{prefix}:{hashlib.sha256(ip.encode()).hexdigest()[:20]}"
            n = cache.get(key, 0)
            if n >= limit:
                return JsonResponse(
                    {"error": "Too many requests. Please wait a moment."},
                    status=429,
                )
            cache.set(key, n + 1, window_seconds)
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


def rate_limit_or_response(request, prefix: str, limit: int = 40, window_seconds: int = 120):
    """Return JsonResponse 429 if over limit, else None (caller increments by side effect)."""
    ip = get_client_ip(request)
    key = f"rl:{prefix}:{hashlib.sha256(ip.encode()).hexdigest()[:20]}"
    n = cache.get(key, 0)
    if n >= limit:
        return JsonResponse(
            {"error": "Upload rate limit exceeded. Try again shortly."},
            status=429,
        )
    cache.set(key, n + 1, window_seconds)
    return None
