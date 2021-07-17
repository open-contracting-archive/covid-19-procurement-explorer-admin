from django.db import models
from django.utils.translation import gettext_lazy as _

from country.models.buyer import Buyer
from country.models.country import Country
from country.models.equity_category import EquityCategory
from country.models.red_flag import RedFlag
from country.models.supplier import Supplier
from country.models.temp_data_import_table import TempDataImportTable


class Tender(models.Model):
    PROCUREMENT_METHOD_CHOICES = [
        ("open", "open"),
        ("limited", "limited"),
        ("direct", "direct"),
        ("selective", "selective"),
    ]

    TENDER_STATUS_CHOICES = [
        ("active", "active"),
        ("completed", "completed"),
        ("canceled", "canceled"),
    ]

    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="tenders")
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="tenders", null=True, blank=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name="tenders", null=True, blank=True)

    contract_id = models.CharField(verbose_name=_("Contract ID"), max_length=150, null=True)
    contract_date = models.DateField(verbose_name=_("Contract date"), null=True, db_index=True)
    procurement_procedure = models.CharField(
        verbose_name=_("Procurement procedure"), max_length=25, choices=PROCUREMENT_METHOD_CHOICES, null=True
    )
    status = models.CharField(
        verbose_name=_("Contract status"), max_length=25, choices=TENDER_STATUS_CHOICES, null=True
    )
    link_to_contract = models.CharField(verbose_name=_("Link to contract"), max_length=250, null=True, blank=True)
    link_to_tender = models.CharField(verbose_name=_("Link to tender"), max_length=250, null=True, blank=True)
    data_source = models.CharField(verbose_name=_("Data source"), max_length=250, null=True, blank=True)

    no_of_bidders = models.BigIntegerField(verbose_name=_("Number of Bidders"), null=True, blank=True)
    contract_title = models.TextField(verbose_name=_("Contract title"), null=True, blank=True)
    contract_value_local = models.FloatField(verbose_name=_("Contract value local"), null=True, blank=True)
    contract_value_usd = models.FloatField(verbose_name=_("Contract value USD"), null=True, blank=True)
    contract_desc = models.TextField(verbose_name=_("Contract description"), null=True, blank=True)
    tender_value_local = models.FloatField(verbose_name=_("Tender value local"), null=True, blank=True)
    tender_value_usd = models.FloatField(verbose_name=_("Tender value USD"), null=True, blank=True)
    award_value_local = models.FloatField(verbose_name=_("Award value local"), null=True, blank=True)
    award_value_usd = models.FloatField(verbose_name=_("Award value USD"), null=True, blank=True)

    equity_category = models.ManyToManyField(EquityCategory)
    red_flag = models.ManyToManyField(RedFlag)
    temp_table_id = models.ForeignKey(
        TempDataImportTable, on_delete=models.CASCADE, related_name="tenders", null=True, blank=True
    )

    def __str__(self):
        return self.contract_id

    class Meta:
        app_label = "country"
