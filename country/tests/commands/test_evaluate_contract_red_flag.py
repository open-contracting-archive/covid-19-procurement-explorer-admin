from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TransactionTestCase

from country.models import Country


class EvaluateContractRedFlagTests(TransactionTestCase):
    def test_without_country_code(self):
        with self.assertRaises(CommandError):
            call_command("evaluate_contract_red_flag")

    def test_with_country_code(self):
        Country.objects.all().delete()
        Country.objects.create(name="Mexico", country_code="MEX", country_code_alpha_2="MX", currency="MXN")
        self.assertEquals(call_command("evaluate_contract_red_flag", "mx"), None)
