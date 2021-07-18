from django.core.management.base import BaseCommand
from django.db.models import Q

from country.models import GoodsServices
from country.tasks import process_currency_conversion


class Command(BaseCommand):
    help = "Convert contract local amount values into USD"

    def handle(self, *args, **kwargs):
        self.stdout.write("Processing currency conversion")
        unconverted_tender = GoodsServices.objects.filter(
            Q(tender_value_usd__isnull=True) | Q(award_value_usd__isnull=True) | Q(contract_value_usd__isnull=True)
        )

        for tender in unconverted_tender:
            id = tender.id
            tender_date = tender.contract.contract_date
            tender_value_local = tender.tender_value_local
            contract_value_local = tender.contract_value_local
            award_value_local = tender.award_value_local
            currency = tender.country.currency
            process_currency_conversion.apply_async(
                args=(tender_value_local, award_value_local, contract_value_local, tender_date, currency, id),
                queue="covid19",
            )
            self.stdout.write("Created task for id :" + str(id))
        self.stdout.write("Done")
