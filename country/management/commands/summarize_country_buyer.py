from django.core.management.base import BaseCommand

from country.models import Buyer, Country
from country.tasks import summarize_buyer


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("country", type=str)

    def handle(self, *args, **kwargs):
        country_alpha_code = kwargs["country"]
        try:
            country = Country.objects.get(country_code_alpha_2=country_alpha_code)
        except Exception:
            return self.stdout.write("Country alpha code doesnt exist")
        buyers = Buyer.objects.filter(tenders__country=country)
        for buyer in buyers:
            self.stdout.write("Created tasks for buyer_id" + str(buyer.id))
            summarize_buyer.apply_async(args=(buyer.id,), queue="covid19")
