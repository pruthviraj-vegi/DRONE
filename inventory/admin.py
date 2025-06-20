from django.contrib import admin
from .models import Inventory, StockTransaction


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "part_name",
        "barcode",
        "quantity",
        "minimum_quantity",
        "supplier",
        "is_active",
        "created_at",
        "updated_at",
    )
    search_fields = ("company_name", "part_name", "barcode")
    list_filter = ("supplier", "is_active")
    autocomplete_fields = ("supplier",)


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "inventory",
        "transaction_type",
        "quantity_change",
        "previous_quantity",
        "new_quantity",
        "created_at",
        "created_by",
    )
    search_fields = (
        "inventory__part_name",
        "inventory__barcode",
        "created_by__username",
    )
    list_filter = ("transaction_type", "created_at", "inventory__supplier")
    autocomplete_fields = ("inventory",)
