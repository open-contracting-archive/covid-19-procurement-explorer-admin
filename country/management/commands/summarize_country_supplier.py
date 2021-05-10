from django.core.management.base import BaseCommand

from country.models import Country, Supplier
from country.tasks import summarize_supplier


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("country", type=str)

    def handle(self, *args, **kwargs):
        country_alpha_code = kwargs["country"]
        try:
            country = Country.objects.get(country_code_alpha_2=country_alpha_code)
        except Exception:
            return self.stdout.write("Country alpha code doesnt exist")
        suppliers = Supplier.objects.filter(tenders__country=country)
        for supplier in suppliers:
            self.stdout.write("Created tasks for supplier_id" + str(supplier.id))
            summarize_supplier.apply_async(args=(supplier.id,), queue="covid19")
