from django.db import models
from django.utils.translation import gettext_lazy as _

from core import model_mixins


class ImageGallery(model_mixins.CreatedUpdatedDateMixin):
    name = models.CharField(_('name'), null=True, max_length=255)
    image = models.ImageField(_('image'), upload_to='gallery/')

    class Meta:
        verbose_name = _('Image')
        verbose_name_plural = _('Images')

    def __str__(self):
        return self.name
