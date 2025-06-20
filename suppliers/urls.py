from django.urls import path
from . import views

app_name = "suppliers"

urlpatterns = [
    path("", views.supplier_list, name="supplier_list"),
    path("create/", views.CreateSupplier.as_view(), name="supplier_create"),
    path("<int:pk>/edit/", views.EditSupplier.as_view(), name="supplier_edit"),
    path("<int:pk>/delete/", views.supplier_delete, name="supplier_delete"),
]
