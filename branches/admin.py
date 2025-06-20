from django.contrib import admin
from .models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "parent", "is_active", "created_at", "updated_at")
    search_fields = ("name", "address", "phone", "email")
    list_filter = ("type", "is_active")
    autocomplete_fields = ("parent",)
