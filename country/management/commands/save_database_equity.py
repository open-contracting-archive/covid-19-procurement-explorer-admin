from django.core.management.base import BaseCommand

from country.models import Country
from country.tasks import fetch_equity_data


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("country", type=str, help="Country name for equity category")

    def handle(self, *args, **kwargs):
        country_name = kwargs["country"]
        print(f"Fetching equity data for {country_name}")
        if country_name:
            try:
                if Country.objects.filter(name=country_name).exists():
                    fetch_equity_data.apply_async(args=(country_name,), queue="covid19")
                    print(print("Created task: import_equity_data"))
            except Exception as e:
                print(e)

        else:
            print("Enter country name as arguments")
        return "Done"
