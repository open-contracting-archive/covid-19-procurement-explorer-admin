from django.db import models
from django.utils.translation import gettext_lazy as _


class RedFlag(models.Model):
    title = models.CharField(
        verbose_name=_("Title"),
        max_length=250,
        null=True,
        blank=True,
        db_index=True,
        help_text=_("A short description of the red flag, as shown in the frontend."),
    )
    description = models.CharField(
        verbose_name=_("Description"), max_length=300, null=True, blank=True, db_index=True, help_text=_("Not used.")
    )
    function_name = models.CharField(
        verbose_name=_("Function"),
        max_length=300,
        null=True,
        blank=True,
        db_index=True,
        help_text=_("This corresponds to a function in the code. Do not edit it unless you are a developer."),
    )
    implemented = models.BooleanField(
        null=True,
        blank=True,
        default=False,
        help_text=_("Display the red flag. Do not enable unless you know the red flag is implemented."),
    )

    def __str__(self):
        return self.title

    class Meta:
        app_label = "country"
