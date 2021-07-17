from django.db import models
from django.utils.translation import gettext_lazy as _


class CurrencyConversionCache(models.Model):
    source_currency = models.CharField(verbose_name=_("Source currency"), max_length=50, null=True)
    dst_currency = models.CharField(verbose_name=_("Dst currency"), max_length=50, null=True)
    conversion_date = models.DateField(verbose_name=_("Conversion date"), null=True)
    conversion_rate = models.FloatField(verbose_name=_("Conversion rate"), null=True)

    class Meta:
        app_label = "country"
