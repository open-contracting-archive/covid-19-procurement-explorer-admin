from django.core.management import CommandError, call_command
from django.test import TransactionTestCase


class GenerateCountryContractExcelTests(TransactionTestCase):
    def test_command(self):
        with self.assertRaises(CommandError):
            call_command("generate_country_contract_excel")

    def test_command_with_country(self):
        self.assertEquals(call_command("generate_country_contract_excel", "MX"), None)
