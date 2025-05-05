from django.contrib import admin
from django.utils.safestring import mark_safe
from nested_admin.nested import NestedTabularInline, NestedModelAdmin
from analytics.models import ActivityStatistics, Supervision, Comment, CommentImage, CommentFiles
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
        return [(item.id, item) for item in Supervision.objects.all()[:self.LIMIT_COUNT]]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(supervision__id=self.value())
        return queryset


@admin.register(ActivityStatistics)
class ActivityStatisticsAdmin(admin.ModelAdmin):
    list_display = ('id', 'activity__name', 'activity__activity_group__name', 'supervision__organization__name',
                    'start_date', 'end_date', 'delta', )
    readonly_fields = ('delta',)
    list_filter = (ActivityStatisticsOrganizationFilter, ActivityStatisticsSupervisionFilter, 'activity',)

    def has_add_permission(self, request):
        return False


class CommentImageInline(NestedTabularInline):
    model = CommentImage
    extra = 0
    fields = ('image', ) + admin_mixins.ImagePreviewAdminMixin.fields
    readonly_fields = admin_mixins.ImagePreviewAdminMixin.readonly_fields

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="100">')

        return "[no image]"


class CommentFileInline(NestedTabularInline):
    model = CommentFiles
    extra = 0
    fields = ('file', )


class CommentsAdminInline(NestedTabularInline):
    model = Comment
    extra = 0
    inlines = (CommentImageInline, CommentFileInline)
    fields = ('text', 'created_date', 'updated_date') + admin_mixins.CreatedByUpdatedByAdminMixin.fields
    readonly_fields = ('created_date', 'updated_date') + admin_mixins.CreatedByUpdatedByAdminMixin.readonly_fields


@admin.register(Supervision)
class SupervisionAdmin(NestedModelAdmin):
    list_display = ('id', 'name', 'organization', 'user', 'start_date', 'end_date', 'delta', 'valid')
    readonly_fields = ('delta', 'start_date', 'end_date') + admin_mixins.CreatedByUpdatedByAdminMixin.readonly_fields + (
    'updated_date', 'created_date', 'linked_activity_table')
    list_filter = ('organization',)
    fields = ('name', 'organization', 'user', 'worker', 'start_date', 'end_date') + admin_mixins.CreatedByUpdatedByAdminMixin.fields + ('linked_activity_table',)
    inlines = (CommentsAdminInline,)

    def has_add_permission(self, request):
        return False

    def linked_activity_table(self, obj):
        rows = "".join(f"<tr><td>{item.activity.name}</td><td>{item.end_date - item.start_date}</td></tr>" for item in obj.statistics.all())
        html = f"<table><thead><tr><th>Activity name</th><th>Delta</th></tr></thead><tbody>{rows}</tbody></table>"
        return mark_safe(html)

    linked_activity_table.short_description = "Statistics"
