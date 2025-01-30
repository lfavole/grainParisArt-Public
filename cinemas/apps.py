from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class CinemasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cinemas"
    verbose_name = _("Cinemas")

    def ready(self):
        from .models import Theater

        for theater in settings.THEATERS_JSON:
            settings.THEATERS.append(
                Theater(
                    theater["id"],
                    theater["name"],
                    theater["latitude"],
                    theater["longitude"],
                )
            )
