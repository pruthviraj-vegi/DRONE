from django.urls import path
from . import views

app_name = "invoice"

urlpatterns = [
    path(
        "<int:session_id>/select-details/",
        views.select_details,
        name="select_details",
    ),
    path("", views.invoice_list, name="invoice_list"),
    path("fetch/", views.fetch_invoice, name="fetch_invoice"),
    path("<int:invoice_id>/", views.invoice_detail, name="invoice_detail"),
    path(
        "<int:invoice_id>/edit/",
        views.InvoiceEditView.as_view(),
        name="invoice_edit",
    ),
]
