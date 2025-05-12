from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from nested_admin.nested import NestedTabularInline, NestedModelAdmin
from analytics.models import ActivityStatistics, Supervision, Comment, CommentImage, CommentFiles, Failure
from django.utils.translation import gettext_lazy as _

from core import admin_mixins
from core.models import Organization


class ActivityStatisticsOrganizationFilter(admin.SimpleListFilter):
    title = _('organization')
    parameter_name = 'organization'

    def lookups(self, request, model_admin):
        return [(item.id, item.name) for item in Organization.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(supervision__organization__id=self.value())
        return queryset


class ActivityStatisticsSupervisionFilter(admin.SimpleListFilter):
    title = _('last supervisions')
    parameter_name = 'last_supervisions'

    LIMIT_COUNT = 10

    def lookups(self, request, model_admin):
        return [(item.id, item) for item in Supervision.objects.order_by('-start_date')[:self.LIMIT_COUNT]]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(supervision__id=self.value())
        return queryset


class CommentImageInline(NestedTabularInline):
    model = CommentImage
    extra = 0
    fields = ('image',) + admin_mixins.ImagePreviewAdminMixin.fields
    readonly_fields = admin_mixins.ImagePreviewAdminMixin.readonly_fields

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="100">')

        return "[no image]"


class CommentFileInline(NestedTabularInline):
    model = CommentFiles
    extra = 0
    fields = ('file',)


class CommentsAdminInline(NestedTabularInline):
    model = Comment
    extra = 0
    inlines = (CommentImageInline, CommentFileInline)
    fields = ('text', 'created_date', 'created_by')
    readonly_fields = ('created_date', 'updated_date') + admin_mixins.CreatedByUpdatedByAdminMixin.readonly_fields


@admin.register(ActivityStatistics)
class ActivityStatisticsAdmin(admin_mixins.LocalizedDateTimeAdminMixin, NestedModelAdmin):
    list_display = ('id', 'activity__name', 'activity__activity_group__name', 'supervision__organization__name',
                    'start_date', 'end_date', 'delta', 'is_valid')
    readonly_fields = (
    'supervision', 'activity', 'created_by', 'updated_by', 'created_date', 'updated_date', 'start_date', 'end_date',
    'delta', 'is_valid', 'failure')
    fields = ('activity', 'start_date', 'end_date', 'delta', 'failure')
    list_filter = (ActivityStatisticsOrganizationFilter, ActivityStatisticsSupervisionFilter, 'activity',)

    inlines = (CommentsAdminInline,)

    def has_add_permission(self, request):
        return False

    def is_valid(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if not obj.failure else 'red',
            '✓' if not obj.failure else '✗ Failure in system'
        )

    is_valid.short_description = _('Absence of a system failure')


@admin.register(Supervision)
class SupervisionAdmin(admin_mixins.LocalizedDateTimeAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'organization', 'user', 'start_date', 'end_date', 'delta', 'is_valid')
    readonly_fields = (
                      'delta', 'start_date', 'end_date') + admin_mixins.CreatedByUpdatedByAdminMixin.readonly_fields + (
                          'updated_date', 'created_date', 'linked_activity_table')
    list_filter = ('organization',)
    fields = ('organization', 'user', 'worker', 'start_date',
              'end_date') + admin_mixins.CreatedByUpdatedByAdminMixin.fields + ('linked_activity_table',)

    def is_valid(self, obj):
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if obj.validity else 'red',
            '✓' if obj.validity else '✗ Failure in system'
        )

    is_valid.short_description = _('Absence of a system failure')

    def has_add_permission(self, request):
        return False

    def linked_activity_table(self, obj):
        rows = "".join(f"<tr><td>{item.activity.name}</td><td>{item.delta}</td></tr>" for item in
                       obj.statistics.all())
        html = f"<table><thead><tr><th>Activity name</th><th>Delta</th></tr></thead><tbody>{rows}</tbody></table>"
        return mark_safe(html)

    linked_activity_table.short_description = "Statistics"


@admin.register(Failure)
class FailureAdmin(admin_mixins.LocalizedDateTimeAdminMixin, admin.ModelAdmin):
    readonly_fields = ('start_date', 'end_date')
