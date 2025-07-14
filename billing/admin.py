from django.contrib import admin
from .models import BillingSession, BillingSessionItem


class BillingSessionItemInline(admin.TabularInline):
    model = BillingSessionItem
    extra = 0
    fields = ("inventory", "quantity", "price", "amount", "created_at", "updated_at")
    readonly_fields = ("amount", "created_at", "updated_at")


class BillingSessionAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at", "is_active", "total_amount")
    list_filter = ("is_active", "created_at", "user")
    search_fields = ("name", "user__username")
    inlines = [BillingSessionItemInline]
    readonly_fields = ("created_at",)


admin.site.register(BillingSession, BillingSessionAdmin)


class BillingSessionItemAdmin(admin.ModelAdmin):
    list_display = (
        "session",
        "inventory",
        "quantity",
        "price",
        "amount",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "inventory")
    search_fields = ("session__name", "inventory__part_name")
    readonly_fields = ("amount", "created_at", "updated_at")


admin.site.register(BillingSessionItem, BillingSessionItemAdmin)
