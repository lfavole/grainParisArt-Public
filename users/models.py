from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

# Create your models here.

class User(AbstractUser):
    """
    User model for model swapping.

    It's here if we might need to change the user model and don't want to unapply the migrations.

    See https://docs.djangoproject.com/en/5.1/topics/auth/customizing/#changing-to-a-custom-user-model-mid-project.
    """

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        permissions = [
            ("can_see_debug_toolbar", _("Can see debug toolbar")),
        ]
        swappable = "AUTH_USER_MODEL"
