from django.core.management import CommandError, call_command
from django.test import TransactionTestCase


class SaveDatabaseEquityCommand(TransactionTestCase):
    def test_command_without_country_batch(self):
        with self.assertRaises(CommandError):
            call_command("save_database_equity")
