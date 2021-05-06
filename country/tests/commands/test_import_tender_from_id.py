from django.core.management import CommandError, call_command
from django.test import TransactionTestCase


class TenderImportCommand(TransactionTestCase):
    def test_command_without_country_batch(self):
        with self.assertRaises(CommandError):
            call_command("import_tender_from_id")
