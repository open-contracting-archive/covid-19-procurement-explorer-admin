from django.core.management import call_command
from django.test import TransactionTestCase


class ProcessCurrencyConversionCommandTest(TransactionTestCase):
    def test_command(self):
        self.assertEquals(call_command("process_currency_conversion"), None)
