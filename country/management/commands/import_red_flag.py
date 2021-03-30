from django.core.management.base import BaseCommand

from country.models import Tender
from country.tasks import clear_redflag, process_redflag, process_redflag6, process_redflag7


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        print("Removing all the relations of Red flag")
        tenders = Tender.objects.all()
        for tender in tenders:
            id = tender.id
            clear_redflag.apply_async(args=(id,), queue="covid19")

        print("All cleared")
        print("Processing Red Flag in tender")

        tender_instance = Tender.objects.filter(supplier__isnull=False, buyer__isnull=False).values(
            "id", "buyer__buyer_name", "supplier__supplier_name", "supplier__supplier_address"
        )
        for tender in tender_instance:
            id = tender["id"]
            process_redflag7.apply_async(args=(id, tender), queue="covid19")
            process_redflag6.apply_async(args=(id, tender), queue="covid19")

        for tender in tenders:
            id = tender.id
            process_redflag.apply_async(args=(id,), queue="covid19")
            print("Created task for id :" + str(id))
        return "Done"
