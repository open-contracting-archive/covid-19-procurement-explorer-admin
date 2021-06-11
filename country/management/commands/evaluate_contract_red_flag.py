from django.core.management.base import BaseCommand

from country.models import Country, Tender
from country.tasks import clear_redflag, process_redflag, process_redflag6, process_redflag7


class Command(BaseCommand):
    help = "Compute red flag for specific country"

    def add_arguments(self, parser):
        parser.add_argument("country", nargs="+", type=str)

    def handle(self, *args, **options):
        country_code = options["country"][0]
        country_code = str(country_code).upper()
        country_list = Country.objects.exclude(country_code_alpha_2="gl").values_list(
            "country_code_alpha_2", flat=True
        )

        if country_code not in country_list:
            self.stderr.write("Country code is invalid.")
            return

        country = Country.objects.get(country_code_alpha_2=country_code)

        self.stdout.write(f"Processing Red flag for {country.name}")

        country_tenders = Tender.objects.filter(
            country_id=country.id, supplier__isnull=False, buyer__isnull=False
        ).values("id", "buyer__buyer_name", "supplier__supplier_name", "supplier__supplier_address")

        for tender in country_tenders:
            tender_id = tender["id"]
            self.stdout.write("Created task for id :" + str(tender_id))
            clear_redflag.apply_async(args=(tender_id,), queue="covid19")
            process_redflag6.apply_async(args=(tender_id,), queue="covid19")
            process_redflag7.apply_async(args=(tender_id,), queue="covid19")
            process_redflag.apply_async(args=(tender_id,), queue="covid19")

        self.stdout.write("Done")
