from django.contrib import admin
from django.contrib.auth import admin as auth_admin

from users.models import User
from django.utils.translation import gettext_lazy as _


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "email")}),
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
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
        (_("Worker info"), {"fields": ("classifier", "organization")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "classifier",
                    "organization",
                ),
            },
        ),
    )
    list_display = ["username", "first_name", "last_name", "is_superuser"]
    search_fields = ["first_name", "last_name"]
