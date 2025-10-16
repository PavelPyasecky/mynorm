from django.db import models
from django.utils.translation import gettext_lazy as _


class AppSetting(models.Model):
    """
    Singleton model for application settings.
    Only one instance should exist for the entire application.
    """
    hide_failure_btn = models.BooleanField(
        default=False, 
        verbose_name=_("hide failure button"), 
        help_text=_('Hide failure button display')
    )
    hide_info_btn = models.BooleanField(
        default=False, 
        verbose_name=_("hide info button"), 
        help_text=_('Hide info button display')
    )
    
    class Meta:
        verbose_name = _("Application Settings")
        verbose_name_plural = _("Application Settings")
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure only one instance exists.
        """
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """
        Prevent deletion of the singleton instance.
        """
        pass
    
    @classmethod
    def load(cls):
        """
        Get or create the singleton instance.
        """
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
    
    def __str__(self):
        return "Application Settings"
