from django.core.management.base import BaseCommand

from country.tasks import country_contract_excel


class Command(BaseCommand):
    help = "Generate Country Contract Excel"

    def add_arguments(self, parser):
        parser.add_argument("country", type=str)

    def handle(self, *args, **kwargs):
        country = kwargs["country"]
        country_contract_excel.apply_async(args=(country,), queue="covid19")
