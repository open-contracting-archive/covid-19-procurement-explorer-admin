from django.core.management.base import BaseCommand

from country.models import Country
from country.tasks import evaluate_contract_red_flag


class Command(BaseCommand):
    help = "Compute red flag for specific country"

    def add_arguments(self, parser):
        parser.add_argument("country", type=str)

    def handle(self, *args, **kwargs):
        country_alpha_code = kwargs["country"].upper()
        try:
            Country.objects.get(country_code_alpha_2=country_alpha_code)
        except Exception:
            return self.stdout.write("Country alpha code doesnt exist")
        evaluate_contract_red_flag.apply_async(
            args=(country_alpha_code,),
            queue="covid19",
        )
        return "Done"
