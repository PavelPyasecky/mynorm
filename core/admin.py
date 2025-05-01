from django.contrib import admin

from core import admin_mixins
from core.models import Organization, Classifier


@admin.register(Organization)
class OrganizationAdmin(admin_mixins.CreatedByUpdatedByAdminMixin):
    list_display = (
        "name",
    )
    search_fields = ("name",)
    fields = (
            ("name",)
            + admin_mixins.CreatedByUpdatedByAdminMixin.fields
    )
    readonly_fields = admin_mixins.CreatedByUpdatedByAdminMixin.readonly_fields


@admin.register(Classifier)
class ClassifierAdmin(admin_mixins.CreatedByUpdatedByAdminMixin):
    list_display = (
        "code", "name"
    )
    search_fields = ("code", "name")
    fields = (
            ("code", "name",)
            + admin_mixins.CreatedByUpdatedByAdminMixin.fields
    )
    readonly_fields = admin_mixins.CreatedByUpdatedByAdminMixin.readonly_fields
