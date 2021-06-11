from django.core.management import CommandError, call_command
from django.test import TransactionTestCase

from country.models import Country


def setUpModule():
    Country.objects.all().delete()
    Country.objects.create(name="Mexico", country_code="MEX", country_code_alpha_2="MX", currency="MXN")


class SaveDatabaseEquityCommand(TransactionTestCase):
    def test_command_without_country_batch(self):
        with self.assertRaises(CommandError):
            call_command("save_database_equity")

    def test_command_with_country_batch(self):
        self.assertEquals(call_command("save_database_equity", "Mexico"), None)

    def test_command_with_wrong_country_batch(self):
        self.assertEquals(call_command("save_database_equity", "no_country"), None)
