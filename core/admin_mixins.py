from django.conf import settings
from django.contrib import admin
from django.utils import timezone
from django.utils.formats import localize
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class ImagePreviewAdminMixin(admin.ModelAdmin):
    list_display = ("list_image_preview",)
    fields = ("image_preview",)
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="300">')

        return "[no image]"

    def list_image_preview(self, obj):
        image = getattr(obj, "image", None)
        if image:
            return mark_safe(f'<img src="{image.url}" height="100">')
        return "[no image]"


class CreatedByUpdatedByAdminMixin(admin.ModelAdmin):
    fields = ("created_by", "updated_by")
    readonly_fields = ("created_by", "updated_by")

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for instance in instances:
            instance.created_by = request.user
            instance.updated_by = request.user
            instance.save()

        formset.save_m2m()


class ImagesInlineAdminMixin(admin.TabularInline):
    model = None

    fields = ("image", "image_preview")
    readonly_fields = ("image_preview",)
    extra = 1
    verbose_name = _("Gallery")

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="100">')

        return "[no image]"


class VideosInlineAdminMixin(admin.TabularInline):
    model = None

    extra = 1
    fields = ("video_file", "video_preview")
    readonly_fields = ("video_preview",)

    @admin.display(
        description=_("Preview"),
    )
    def video_preview(self, obj):
        if obj.video_file:
            return mark_safe(
                f'<video width="400" height="230" controls>'
                f'<source src="{obj.video_file.url}" type="video/mp4">'
                f"Your browser does not support the video tag."
                f"</video>",
            )
        return "No video uploaded"


class VideoAdminMixin(admin.ModelAdmin):
    fields = ("video_file", "video_preview")
    readonly_fields = ("video_preview",)

    @admin.display(description=_("Preview"))
    def video_preview(self, obj):
        if obj.video_file:
            return mark_safe(
                f'<video width="400" height="230" controls>'
                f'<source src="{obj.video_file.url}" type="video/mp4">'
                f"Your browser does not support the video tag."
                f"</video>",
            )
        return "No video uploaded"


class LocalizedDateTimeAdminMixin:
    def changelist_view(self, request, extra_context=None):
        timezone.activate(settings.ADMIN_TIME_ZONE)
        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        timezone.activate(settings.ADMIN_TIME_ZONE)
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        return [self.localize_datetime_field(
            field) if field in self.model._meta.get_fields() and field.get_internal_type() == 'DateTimeField' else field
                for field in list_display]

    def localize_datetime_field(self, field_name):
        def wrapper(obj):
            dt = getattr(obj, field_name)
            return localize(timezone.localtime(dt)) if dt else ""

        wrapper.short_description = field_name
        wrapper.admin_order_field = field_name
        return wrapper
