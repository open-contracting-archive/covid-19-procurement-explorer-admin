from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TransactionTestCase

from country.models import Buyer, Country, Supplier, Tender

command_name = "evaluate_contract_red_flag"


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


class EvaluateContractRedFlagTest(TransactionTestCase):
    def test_without_country_code(self):
        with self.assertRaises(CommandError):
            call_command(command_name)

    def test_with_country_code(self):
        self.assertEquals(call_command(command_name, "MX"), "Done")

    def test_with_country_wrong_code(self):
        self.assertEquals(call_command(command_name, "mxss"), None)
