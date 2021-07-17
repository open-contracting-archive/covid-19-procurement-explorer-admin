from django.core.management import CommandError, call_command
from django.test import TransactionTestCase

command_name = "export_country_contracts"


class ExportCountryContractsTest(TransactionTestCase):
    def test_command(self):
        with self.assertRaises(CommandError):
            call_command(command_name)

    def test_command_with_country(self):
        self.assertEquals(call_command(command_name, "MX"), None)
