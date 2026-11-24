from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _


@admin.register(get_user_model())
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Other information"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                    "uuid",
                    "department_name",
                    "ad_groups",
                    "last_api_use",
                ),
                "classes": ["collapse"],
            },
        ),
    )
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_superuser",
        "is_active",
        "uuid",
        "date_joined",
        "last_login",
    )
    list_filter = (
        "date_joined",
        "last_login",
        "is_staff",
        "is_superuser",
        "is_active",
        "groups",
        "ad_groups",
    )
    search_fields = (*DjangoUserAdmin.search_fields, "uuid")
    filter_horizontal = (*DjangoUserAdmin.filter_horizontal, "ad_groups")
    readonly_fields = (
        "last_login",
        "date_joined",
        "uuid",
        "last_api_use",
    )
    ordering = ("-date_joined",)
    date_hierarchy = "date_joined"
