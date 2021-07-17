from django.core.management.base import BaseCommand

from country.models import Country
from country.tasks import evaluate_contract_equity


class Command(BaseCommand):
    help = "Evaluate country contracts for equity indicators"

    def add_arguments(self, parser):
        parser.add_argument("country_code", type=str, help="Country code")

    def handle(self, *args, **kwargs):
        country_code = kwargs["country_code"].upper()

        try:
            Country.objects.get(country_code_alpha_2=country_code)
        except Exception:
            return self.stdout.write("Invalid country code provided")

        evaluate_contract_equity.apply_async(args=(country_code,), queue="covid19")

        return "Done"
