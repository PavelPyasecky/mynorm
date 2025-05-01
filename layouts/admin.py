from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from ordered_model.admin import OrderedTabularInline, OrderedInlineModelAdminMixin

from core import admin_mixins
from layouts.models import Layout, ActivityGroup, Activity


class ActivityGroupInline(OrderedTabularInline):
    model = ActivityGroup
    extra = 0
    fields = ('name', 'order', 'move_up_down_links',)
    readonly_fields = ('order', 'move_up_down_links',)
    ordering = ('order',)


@admin.register(Layout)
class LayoutAdmin(OrderedInlineModelAdminMixin, admin_mixins.CreatedByUpdatedByAdminMixin):
    inlines = (ActivityGroupInline,)
    fields = (
            ("organization", "classifier",)
            + admin_mixins.CreatedByUpdatedByAdminMixin.fields
    )
    readonly_fields = admin_mixins.CreatedByUpdatedByAdminMixin.readonly_fields
    search_fields = ('id',)


class ActivityInline(OrderedTabularInline):
    model = Activity
    extra = 0
    fields = ('name', 'order', 'move_up_down_links',)
    readonly_fields = ('order', 'move_up_down_links',)
    ordering = ('order',)


@admin.register(ActivityGroup)
class ActivityGroupAdmin(SortableAdminMixin,OrderedInlineModelAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'layout', 'order',)
    fields = ('name', 'layout')
    list_filter = ('layout',)
    autocomplete_fields = ('layout',)
    inlines = (ActivityInline,)
