from django.urls import path
from . import views

app_name = "billing"

urlpatterns = [
    path("sessions/", views.billing_session_list, name="session_list"),
    path("sessions/create/", views.billing_session_create, name="session_create"),
    path(
        "sessions/<int:session_id>/",
        views.billing_session_detail,
        name="session_detail",
    ),
    path(
        "sessions/<int:session_id>/add-item/",
        views.add_item_by_barcode,
        name="add_item_by_barcode",
    ),
    path(
        "sessions/<int:session_id>/update-items/",
        views.update_items,
        name="update_items",
    ),
    path(
        "sessions/<int:item_id>/delete-item/",
        views.delete_item,
        name="delete_item",
    ),
    path(
        "api/items/<int:item_id>/update/",
        views.update_item_api,
        name="update_item_api",
    ),
]
