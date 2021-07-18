from django.db import models
from django.utils.translation import gettext_lazy as _

from country.models import Country, EquityCategory


class EquityKeywords(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="equity_keywords", null=True)
    equity_category = models.ForeignKey(
        EquityCategory, on_delete=models.CASCADE, related_name="equity_keywords", null=True
    )
    keyword = models.CharField(verbose_name=_("Keyword"), max_length=100, null=False)

    class Meta:
        app_label = "country"
