from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from django.utils.safestring import mark_safe

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
    list_display = ('id', 'name', 'organization', 'classifier')
    fields = (
            ('name', "organization", "classifier",)
            + admin_mixins.CreatedByUpdatedByAdminMixin.fields
    )
    readonly_fields = admin_mixins.CreatedByUpdatedByAdminMixin.readonly_fields
    search_fields = ('id', 'name')


class ActivityInline(OrderedTabularInline):
    model = Activity
    extra = 0
    fields = ('name', 'order', 'move_up_down_links',)
    readonly_fields = ('order', 'move_up_down_links',)
    ordering = ('order',)


@admin.register(ActivityGroup)
class ActivityGroupAdmin(SortableAdminMixin, OrderedInlineModelAdminMixin, admin_mixins.ImagePreviewAdminMixin):
    list_display = ('name', 'layout', 'order',)
    fields = ('name', 'layout', 'image') + admin_mixins.ImagePreviewAdminMixin.fields
    list_filter = ('layout',)
    autocomplete_fields = ('layout', 'image')
    inlines = (ActivityInline,)

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.image.url}" height="300">')

        return "[no image]"

    def list_image_preview(self, obj):
        image = getattr(obj, "image", None)
        if image:
            return mark_safe(f'<img src="{image.image.url}" height="100">')
        return "[no image]"
