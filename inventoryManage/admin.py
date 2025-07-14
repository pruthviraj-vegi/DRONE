from django.contrib import admin
from .models import BranchInventory, BranchInventoryTransaction, TransactionDetail


@admin.register(TransactionDetail)
class TransactionDetailAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "from_branch",
        "to_branch",
        "transfered_by",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "name",
        "from_branch__name",
        "to_branch__name",
        "transfered_by__full_name",
    )
    list_filter = ("from_branch", "to_branch")
    autocomplete_fields = ("from_branch", "to_branch", "transfered_by")


@admin.register(BranchInventory)
class BranchInventoryAdmin(admin.ModelAdmin):
    list_display = (
        "inventory",
        "branch",
        "quantity",
        "available_quantity",
        "created_at",
        "updated_at",
    )
    search_fields = ("inventory__item__part_name", "branch__name")
    list_filter = ("branch",)
    autocomplete_fields = ("inventory", "branch")


@admin.register(BranchInventoryTransaction)
class BranchInventoryTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "branch_inventory",
        "transaction_type",
        "quantity",
        "created_at",
    )
    search_fields = (
        "branch_inventory__inventory__item__part_name",
        "branch_inventory__branch__name",
    )
    list_filter = ("transaction_type", "created_at", "branch_inventory__branch")
    autocomplete_fields = ("branch_inventory",)
