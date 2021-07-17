from django.db import models
from django.utils.translation import gettext_lazy as _

from country.models import Country


class Supplier(models.Model):
    supplier_id = models.CharField(verbose_name=_("Supplier ID"), max_length=50, null=True)
    supplier_name = models.CharField(
        verbose_name=_("Supplier name"), max_length=250, null=True, blank=True, db_index=True
    )
    supplier_address = models.CharField(verbose_name=_("Supplier address"), max_length=250, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="suppliers", null=True)
    summary = models.JSONField(null=True)

    def __str__(self):
        return f"{self.supplier_id} - {self.supplier_name}"

    class Meta:
        app_label = "country"
