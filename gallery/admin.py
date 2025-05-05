from django.contrib import admin

from core import admin_mixins
from gallery.models import ImageGallery


@admin.register(ImageGallery)
class GalleryAdmin(admin_mixins.ImagePreviewAdminMixin, admin_mixins.CreatedByUpdatedByAdminMixin):
    list_display = admin_mixins.ImagePreviewAdminMixin.list_display + ('name', 'created_date',)
    fields = ('name', 'image', ) + admin_mixins.ImagePreviewAdminMixin.fields
    search_fields = ('name',)
