from django.contrib import admin
from .models import Branch


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "parent", "is_active")
    list_filter = ("type", "is_active")
    search_fields = ("name",)
