from django.core.management import call_command
from django.test import TransactionTestCase


class FillContractValuesTests(TransactionTestCase):
    def test_command(self):
        self.assertEquals(call_command("fill_contract_values"), None)
