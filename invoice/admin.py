from django.contrib import admin
from .models import Invoice, InvoiceItem


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "invoice_type",
        "sale_user",
        "total_amount",
        "branch",
        "created_at",
        "updated_at",
    )
    search_fields = ("id", "customer__name", "sale_user__username")
    list_filter = ("invoice_type", "created_at", "sale_user")
    autocomplete_fields = ("customer", "sale_user")


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ("invoice", "inventory", "quantity", "price", "purchased_price")
    search_fields = ("invoice__id", "inventory__part_name")
    list_filter = ("inventory",)
    autocomplete_fields = ("invoice",)
