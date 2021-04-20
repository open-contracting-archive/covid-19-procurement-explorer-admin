from django.core.management.base import BaseCommand

from country.models import Tender
from country.tasks import fill_contract_values


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        tenders = Tender.objects.all()
        print("Created task: fill_contract_values")
        for tender in tenders:
            fill_contract_values.apply_async(args=(tender.id,), queue="covid19")
