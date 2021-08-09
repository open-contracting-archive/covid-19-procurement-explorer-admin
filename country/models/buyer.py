from django.db import models
from django.utils.translation import gettext_lazy as _

from country.models.country import Country


class Buyer(models.Model):
    buyer_id = models.CharField(verbose_name=_("Buyer ID"), max_length=250, null=True)
    buyer_name = models.CharField(verbose_name=_("Buyer name"), max_length=250, null=True, blank=True, db_index=True)
    buyer_address = models.TextField(verbose_name=_("Buyer address"), null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="buyers", null=True)
    summary = models.JSONField(null=True)

    def __str__(self):
        return f"{self.buyer_id} - {self.buyer_name}"

    class Meta:
        app_label = "country"
