from django.db import models
from django.utils.translation import gettext_lazy as _

from country.models.country import Country
from country.models.goods_services_category import GoodsServicesCategory
from country.models.tender import Tender


class GoodsServices(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="goods_services", null=True)
    goods_services_category = models.ForeignKey(
        GoodsServicesCategory, on_delete=models.CASCADE, related_name="goods_services", null=True
    )
    contract = models.ForeignKey(Tender, on_delete=models.CASCADE, related_name="goods_services", null=True)

    classification_code = models.CharField(
        verbose_name=_("Classification code"), max_length=100, null=True, blank=True
    )
    no_of_bidders = models.BigIntegerField(verbose_name=_("Number of bidders"), null=True, blank=True)

    contract_title = models.TextField(verbose_name=_("Contract title"), null=True, blank=True)
    contract_desc = models.TextField(verbose_name=_("Contract description"), null=True, blank=True)

    quantity_units = models.CharField(verbose_name=_("Quantity,units"), max_length=1500, null=True)
    ppu_including_vat = models.CharField(verbose_name=_("Price per units including VAT"), max_length=1500, null=True)

    tender_value_local = models.FloatField(verbose_name=_("Tender value local"), null=True, blank=True)
    tender_value_usd = models.FloatField(verbose_name=_("Tender value USD"), null=True, blank=True)
    award_value_local = models.FloatField(verbose_name=_("Award value local"), null=True, blank=True)
    award_value_usd = models.FloatField(verbose_name=_("Award value USD"), null=True, blank=True)
    contract_value_local = models.FloatField(
        verbose_name=_("Contract value local"), null=True, blank=True, db_index=True
    )
    contract_value_usd = models.FloatField(verbose_name=_("Contract value USD"), null=True, blank=True, db_index=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        app_label = "country"
