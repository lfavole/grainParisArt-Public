from django.conf import settings
from django.db import models
from django.forms.fields import ChoiceField
from django.utils.translation import gettext_lazy as _


class TheaterField(models.CharField):
    """A field that stores a theater ID and displays a dropdown of theaters."""

    def __init__(self, *args, **kwargs):
        kwargs["choices"] = self._get_choices()
        kwargs["max_length"] = 10
        kwargs["verbose_name"] = _("Theater")
        super().__init__(*args, **kwargs)

    def _get_choices(self):
        return [(str(theater.id), theater.name) for theater in settings.THEATERS]

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["choices"]
        del kwargs["max_length"]
        del kwargs["verbose_name"]
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        # re-initialize the choices list if it is empty
        # (when the field is instantiated for the first time, the choices list is empty)
        self.choices = self.choices or self._get_choices()
        return super().formfield(**{
            "form_class": ChoiceField,
            **kwargs,
        })
