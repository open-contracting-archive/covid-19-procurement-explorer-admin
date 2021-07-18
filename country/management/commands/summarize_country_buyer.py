from django.core.management.base import BaseCommand

from country.models import Buyer, Country
from country.tasks import summarize_buyer


class Command(BaseCommand):
    help = "Summarize country buyer's contract information"

    def add_arguments(self, parser):
        parser.add_argument("country_code", type=str, help="Country code")

    def handle(self, *args, **kwargs):
        country_code = kwargs["country_code"].upper()
        try:
            country = Country.objects.get(country_code_alpha_2=country_code)
        except Exception:
            return self.stdout.write("Invalid country code provided")

        buyers = Buyer.objects.filter(country=country)

        for buyer in buyers:
            self.stdout.write("Created tasks for buyer_id " + str(buyer.id))
            summarize_buyer.apply_async(args=(buyer.id,), queue="covid19")

        return "Done"
