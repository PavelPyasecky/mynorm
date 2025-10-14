from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = _("users")

    def ready(self):
        from users import signals
        post_migrate.connect(signals.create_default_groups, sender=self)
