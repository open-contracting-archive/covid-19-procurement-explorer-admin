from django.db import models
from django.utils.translation import gettext_lazy as _

from country.models.import_batch import ImportBatch


class TempDataImportTable(models.Model):
    import_batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="import_batch", null=True)
    contract_id = models.CharField(verbose_name=_("Contract Id"), max_length=1500, null=True)
    contract_date = models.CharField(verbose_name=_("Contract date"), max_length=1500, null=True)
    procurement_procedure = models.CharField(verbose_name=_("Procurement procedure"), max_length=1500, null=True)
    procurement_process = models.CharField(verbose_name=_("Procurement process"), max_length=1500, null=True)
    goods_services = models.CharField(verbose_name=_("Goods/Services"), max_length=1500, null=True)
    cpv_code_clear = models.CharField(verbose_name=_("CPV code clear"), max_length=1500, null=True)
    quantity_units = models.CharField(verbose_name=_("Quantity,units"), max_length=1500, null=True)
    ppu_including_vat = models.CharField(verbose_name=_("Price per units including VAT"), max_length=1500, null=True)
    tender_value = models.CharField(verbose_name=_("Tender value"), max_length=1500, null=True)
    award_value = models.CharField(verbose_name=_("Award value"), max_length=1500, null=True)
    contract_value = models.TextField(verbose_name=_("Contract value"), null=True)
    contract_title = models.TextField(verbose_name=_("Contract title"), null=True)
    contract_description = models.TextField(verbose_name=_("Contract description"), null=True)
    no_of_bidders = models.CharField(verbose_name=_("No of bidders"), max_length=1500, null=True)
    buyer = models.CharField(verbose_name=_("Buyer"), max_length=1500, null=True)
    buyer_id = models.CharField(verbose_name=_("Buyer ID"), max_length=150, null=True)
    buyer_address_as_an_object = models.CharField(
        verbose_name=_("Buyer Address(as an object)"), max_length=1500, null=True
    )
    supplier = models.CharField(verbose_name=_("Supplier"), max_length=1500, null=True)
    supplier_id = models.CharField(verbose_name=_("Supplier ID"), max_length=1500, null=True)
    supplier_address = models.CharField(verbose_name=_("Supplier Address"), max_length=1500, null=True)
    contract_status = models.CharField(verbose_name=_("Contract Status"), max_length=1500, null=True)
    contract_status_code = models.CharField(verbose_name=_("Contract Status Code"), max_length=1500, null=True)
    link_to_contract = models.TextField(verbose_name=_("Link to Contract"), null=True)
    link_to_tender = models.TextField(verbose_name=_("Link to Tender"), null=True)
    data_source = models.TextField(verbose_name=_("Data Source"), null=True)

    def __str__(self):
        return self.contract_id

    class Meta:
        app_label = "country"
