from django.urls import path
from . import views

app_name = "inventoryManage"

urlpatterns = [
    path(
        "branch-transfer/",
        views.branch_inventory_transfer,
        name="branch_inventory_transfer",
    ),
    path(
        "fetch-transactions/",
        views.fetch_transactions,
        name="fetch_transactions",
    ),
    path(
        "branch-transfer-list/",
        views.branch_inventory_transfer_list,
        name="branch_inventory_transfer_list",
    ),
    path(
        "transaction-details/<int:transaction_id>/",
        views.transaction_details,
        name="transaction_details",
    ),
]
