from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("branches/", include("branches.urls")),
    path("users/", include("users.urls")),
    path("suppliers/", include("suppliers.urls")),
    path("members/", include("customers.urls")),
    path("inventory/", include("inventory.urls")),
    path("inventoryManage/", include("inventoryManage.urls")),
    path("billing/", include("billing.urls")),
    path("invoice/", include("invoice.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("report/", include("report.urls")),
    path("quote/", include("quote.urls")),
    path("", include("base.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
