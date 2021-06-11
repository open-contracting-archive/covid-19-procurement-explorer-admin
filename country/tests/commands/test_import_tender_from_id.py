from django.core.management import CommandError, call_command
from django.test import TransactionTestCase

from country.models import Buyer, Country, Supplier, Tender


def setUpModule():
    Country.objects.all().delete()
    country = Country.objects.create(name="Mexico", country_code="MEX", country_code_alpha_2="MX", currency="MXN")

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

    Tender.objects.create(
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


class TenderImportCommand(TransactionTestCase):
    def test_command_without_country_batch(self):
        with self.assertRaises(CommandError):
            call_command("import_tender_from_id")

    def test_command_with_wrong_country_batch(self):
        with self.assertRaises(AttributeError):
            call_command("import_tender_from_id", "no_country", 1)

    def test_command_with_country_batch(self):
        self.assertEquals(call_command("import_tender_from_id", "Mexico", 1), None)
