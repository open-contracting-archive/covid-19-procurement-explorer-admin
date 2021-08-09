from django.core.management.base import BaseCommand

from country.models import Country, Supplier
from country.tasks import summarize_supplier


class Command(BaseCommand):
    help = "Summarize supplier's contract information"

    def add_arguments(self, parser):
        parser.add_argument("country_code", type=str, help="Country code")

    def handle(self, *args, **kwargs):
        country_code = kwargs["country_code"].upper()

        try:
            country = Country.objects.get(country_code_alpha_2=country_code)
        except Exception:
            return self.stdout.write("Invalid country code provided")

        suppliers = Supplier.objects.filter(country=country)

        for supplier in suppliers:
            self.stdout.write("Created tasks for supplier_id " + str(supplier.id))
            summarize_supplier.apply_async(args=(supplier.id,), queue="covid19")

        return "Done"
