from django.contrib import admin
from .models import Inventory, StockTransaction, ProductAssembly, AssemblyComponent


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


class AssemblyComponentInline(admin.TabularInline):
    model = AssemblyComponent
    extra = 1
    autocomplete_fields = ("inventory_item",)
    fields = ("inventory_item", "quantity_required", "selling_price", "notes")


@admin.register(ProductAssembly)
class ProductAssemblyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "sku",
        "barcode",
        "is_active",
        "branch",
        "created_at",
        "created_by",
    )
    search_fields = ("name", "sku", "barcode")
    list_filter = ("is_active", "branch", "created_at")
    autocomplete_fields = ("created_by", "branch")
    inlines = [AssemblyComponentInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("components")


@admin.register(AssemblyComponent)
class AssemblyComponentAdmin(admin.ModelAdmin):
    list_display = (
        "assembly",
        "inventory_item",
        "quantity_required",
        "selling_price",
        "created_at",
    )
    search_fields = (
        "assembly__name",
        "inventory_item__part_name",
        "inventory_item__barcode",
    )
    list_filter = ("assembly", "created_at")
    autocomplete_fields = ("assembly", "inventory_item")
