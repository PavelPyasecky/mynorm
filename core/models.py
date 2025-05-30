from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.model_mixins import CreatedUpdatedMixin


class Organization(CreatedUpdatedMixin):
    name = models.CharField(verbose_name=_("name"), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")


def validate_integer_string(value):
    if not value.isdigit():
        raise ValidationError("This field must contain only digits.")


validate_code_digits = RegexValidator(r"^\d{18}$", "Enter exactly 18 digits.")


class Classifier(CreatedUpdatedMixin):
    code = models.CharField(
        verbose_name=_("code"),
        max_length=18,
        unique=True,
        validators=[
            validate_code_digits,
        ],
    )
    name = models.CharField(
        verbose_name=_("name"), max_length=255, null=True, blank=True
    )

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _("Classifier")
        verbose_name_plural = _("Classifiers")
