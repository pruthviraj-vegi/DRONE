from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "address", "tax_number", "notes")
    search_fields = ("name", "phone", "address", "tax_number", "notes")
    list_filter = ("tax_number",)
