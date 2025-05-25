from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("users/", include("users.urls")),
    path("branches/", include("branches.urls")),
    path("suppliers/", include("suppliers.urls")),
    path("members/", include("customers.urls")),
    path("inventory/", include("inventory.urls")),
    path("billing/", include("billing.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
