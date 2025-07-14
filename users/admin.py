from django.contrib import admin
from .models import CustomUser
from django.utils.translation import gettext_lazy as _


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "role",
        "branch",
        "is_active",
        "is_staff",
        "date_joined",
    )
    search_fields = ("full_name",)
    list_filter = ("role", "is_active", "is_staff", "branch")
    autocomplete_fields = ("branch",)


# admin.site.register(CustomUser, UserAdmin)
