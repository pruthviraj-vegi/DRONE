from django.contrib import admin
from .models import Inventory, StockTransaction


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = (
        "company_name",
        "part_name",
        "barcode",
        "uom",
        "purchased_price",
        "selling_price",
        "discount",
        "minimum_quantity",
        "gst",
        "is_active",
        "created_at",
        "updated_at",
        "created_by",
        "branch",
    )
    search_fields = ("company_name", "part_name", "barcode")
    list_filter = ("is_active", "gst")
    autocomplete_fields = ("created_by", "branch")


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = (
        "inventory",
        "transaction_type",
        "quantity",
        "created_at",
        "created_by",
    )
    search_fields = (
        "inventory__part_name",
        "inventory__barcode",
        "created_by__username",
    )
    list_filter = ("transaction_type", "created_at")
    autocomplete_fields = ("inventory",)
