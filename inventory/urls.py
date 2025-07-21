from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.inventory_list, name="inventory_list"),
    path("dashboard/", views.inventory_dashboard, name="inventory_dashboard"),
    path("fetch/", views.fetch_inventory, name="fetch_inventory"),
    path("create/", views.inventory_create, name="inventory_create"),
    path("bulk-import/", views.bulk_import, name="bulk_import"),
    path(
        "download-template/", views.download_csv_template, name="download_csv_template"
    ),
    path("<int:pk>/edit/", views.inventory_edit, name="inventory_edit"),
    path("<int:pk>/delete/", views.inventory_delete, name="inventory_delete"),
    path(
        "<int:inventory_id>/transactions/",
        views.stock_transaction_list,
        name="stock_transaction_list",
    ),
    path("<int:inventory_id>/update-stock/", views.update_stock, name="update_stock"),
    path(
        "branch-inventory/", views.branch_inventory_list, name="branch_inventory_list"
    ),
    path(
        "branch-inventory-fetch/",
        views.branch_inventory_fetch,
        name="branch_inventory_fetch",
    ),
]
