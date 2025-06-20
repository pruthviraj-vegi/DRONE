from django.contrib import admin
from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "get_branches", "status", "created_at")
    search_fields = ("name", "phone")
    list_filter = ("branches",)
    autocomplete_fields = ("branches",)

    def get_branches(self, obj):
        return ", ".join([b.name for b in obj.branches.all()])

    get_branches.short_description = "Branches"
