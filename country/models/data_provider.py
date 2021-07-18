from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from country.models import Country


class DataProvider(models.Model):
    alphaSpaces = RegexValidator(r"^[a-zA-Z ]+$", "Only letters and spaces are allowed in the Country Name")
    name = models.CharField(verbose_name=_("Name"), null=False, unique=True, max_length=50, validators=[alphaSpaces])
    country = models.ForeignKey(Country, on_delete=models.CASCADE, blank=False, null=False)
    website = models.URLField(max_length=200)
    logo = models.ImageField(upload_to="dataprovider/logo", height_field=None, width_field=None, max_length=100)
    remark = models.TextField(verbose_name=_("Remark"), null=False, unique=True, max_length=500000)

    class Meta:
        verbose_name_plural = _("Data Providers")
        app_label = "country"

    def __str__(self):
        return self.name
