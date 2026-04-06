from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "REC Hive administration"
admin.site.site_title = "REC Hive Admin"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.users.api_urls")),
    path("api/", include("apps.shops.api_urls")),
    path("api/", include("apps.cart.api_urls")),
    path("api/", include("apps.orders.api_urls")),
    path("", include("apps.users.urls")),
    path("", include("apps.shops.urls")),
    path("", include("apps.cart.urls")),
    path("", include("apps.orders.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
