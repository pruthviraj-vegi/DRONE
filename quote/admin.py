from django.contrib import admin
from .models import QuoteSession, QuoteItem, QuoteInventory, QuoteMember


class QuoteItemInline(admin.TabularInline):
    model = QuoteItem
    extra = 0
    fields = ("quote_inventory", "quantity", "price", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")


class QuoteSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "total_amount",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("customer__name",)
    inlines = [QuoteItemInline]
    readonly_fields = ("created_at", "updated_at", "total_amount")


class QuoteItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "quote_session",
        "quote_inventory",
        "quantity",
        "price",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at", "quote_inventory")
    search_fields = ("quote_session__customer__name", "quote_inventory__name")
    readonly_fields = ("created_at", "updated_at")


class QuoteInventoryAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "price",
        "discount",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("created_at", "updated_at")


class QuoteMemberAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "phone", "address", "created_at", "updated_at")
    search_fields = ("name", "phone", "address")
    readonly_fields = ("created_at", "updated_at")


admin.site.register(QuoteSession, QuoteSessionAdmin)
admin.site.register(QuoteItem, QuoteItemAdmin)
admin.site.register(QuoteInventory, QuoteInventoryAdmin)
admin.site.register(QuoteMember, QuoteMemberAdmin)
