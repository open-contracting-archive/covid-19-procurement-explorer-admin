from django.core.management import CommandError, call_command
from django.test import TransactionTestCase

from country.models import Buyer, Country, GoodsServices, GoodsServicesCategory, Supplier, Tender

command_name = "summarize_country_buyer"


def setUpModule():
    Country.objects.all().delete()
    country = Country.objects.create(name="Mexico", country_code="MEX", country_code_alpha_2="MX", currency="MXN")
    category = GoodsServicesCategory.objects.create(
        category_name="name",
        category_desc="desc",
    )
    supplier = Supplier.objects.create(
        supplier_id="1",
        supplier_name="sample supplier",
        supplier_address="kathmandu",
    )

    buyer = Buyer.objects.create(
        buyer_id="1",
        buyer_name="sample buyer",
        buyer_address="kathmandu",
    )

    tender = Tender.objects.create(
        country=country,
        supplier=supplier,
        buyer=buyer,
        contract_id=1,
        contract_date="2021-01-01",
        procurement_procedure="open",
        status="active",
        link_to_contract="http://test.com",
        link_to_tender="http://test.com",
        data_source="http://test.com",
        no_of_bidders=1,
        contract_title="test",
        contract_value_local=1.0,
        contract_value_usd=1.0,
        contract_desc="test description",
        tender_value_local=1.0,
        tender_value_usd=1.0,
        award_value_local=1.0,
        award_value_usd=1.0,
    )

    GoodsServices.objects.create(
        country=country,
        goods_services_category=category,
        contract=tender,
        classification_code="code",
        contract_title="title",
        contract_desc="desc",
        quantity_units=1233,
        ppu_including_vat=1234.0,
        tender_value_local=1234.0,
        tender_value_usd=None,
        award_value_local=1234.0,
        award_value_usd=None,
        contract_value_local=1234.0,
        contract_value_usd=None,
    )


class SummarizeCountryBuyerTest(TransactionTestCase):
    def test_command(self):
        with self.assertRaises(CommandError):
            call_command(command_name)

    def test_command_with_country(self):
        self.assertEquals(call_command(command_name, "MX"), None)
