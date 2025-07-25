from django.urls import path
from . import views

app_name = "report"

urlpatterns = [
    path(
        "invoice/<int:pk>/",
        views.createInvoice,
        name="createInvoice",
    ),
    path("barcode/<int:pk>/", views.createBarcode, name="createBarcode"),
    path("quotation/<int:session_id>/", views.quotation_a4, name="quotation_a4"),
    path(
        "individual-credit-report/<int:pk>/",
        views.individual_credit_report,
        name="individual_credit_report",
    ),
    path("member-report/<int:pk>/", views.member_report, name="member_report"),
]
