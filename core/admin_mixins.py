from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _


class PreviewImageAdminMixin(admin.ModelAdmin):
    list_display = ("list_preview_image_preview",)
    fields = ("preview_image", "preview_image_preview", "image", "image_preview")
    readonly_fields = ("image_preview", "preview_image_preview")

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="300">')

        return "[no image]"

    def preview_image_preview(self, obj):
        if obj.preview_image:
            return mark_safe(f'<img src="{obj.preview_image.url}" height="300">')

        return "[no image]"

    def list_preview_image_preview(self, obj):
        image = getattr(obj, "preview_image", None) or getattr(obj, "image", None)
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
