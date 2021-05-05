from django.core.management import call_command
from django.test import TransactionTestCase


class GenerateExcelSummaryTests(TransactionTestCase):
    def test_command(self):
        self.assertEquals(call_command("generate_excel_summary"), None)
