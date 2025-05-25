from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.inventory_list, name="inventory_list"),
    path("create/", views.inventory_create, name="inventory_create"),
    path("<int:pk>/edit/", views.inventory_edit, name="inventory_edit"),
    path("<int:pk>/delete/", views.inventory_delete, name="inventory_delete"),
    path(
        "<int:inventory_id>/transactions/",
        views.stock_transaction_list,
        name="stock_transaction_list",
    ),
    path("<int:inventory_id>/update-stock/", views.update_stock, name="update_stock"),
]
