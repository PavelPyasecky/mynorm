from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class LayoutsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'layouts'
    verbose_name = _('layouts')
